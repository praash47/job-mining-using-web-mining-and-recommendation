"""
Our backend end points in order to communicate and transfer data to and fro from frontend using HTTP requests and response
"""
import json
import PyPDF2

from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from backend.misc import try_and_pass

from jobdetailsextractor.skills import SkillSet
from jobdetailsextractor.models import Job

from .models import JobSeeker

from .utils import (
    decode_utf,
    jaccard_similarity,
    get_skills_from_string,
    lies_in_salary_range,
    deadline_left,
)


@csrf_exempt
def register(request):
    body = decode_utf(request.body)
    if body["action"] == "username_check":
        username = body["username"]
        if User.objects.filter(username=username).first():
            return JsonResponse({"message": "username exists!"})
        else:
            return JsonResponse({})

    elif body["action"] == "email_needed":
        username = body["username"]
        return JsonResponse({"email": User.objects.get(username=username).email})

    elif body["action"] == "update":
        ousername = body["ousername"]
        username = body["username"]
        email = body["email"]
        skills = body["skills"]
        user = User.objects.get(username=ousername)
        user.username = username
        user.email = email
        user.save()
        jobseeker = JobSeeker.objects.get(user=user)
        jobseeker.skill_set = skills
        jobseeker.save()

        return JsonResponse({"message": "successfully updated!", "user": user.username})

    elif body["action"] == "change_password":
        username = body["username"]
        user = User.objects.get(username=username)
        password = body["password"]
        new_password = make_password(body["new_password"])

        if check_password(password, user.password):
            user.password = new_password
            user.save()
            return JsonResponse({"message": "password change successful"})
        else:
            return JsonResponse({"message": "wrong old password!"})

    elif body["action"] == "skills_insert":
        skills = body["skills"]
        username = body["username"]
        job_seeker = JobSeeker.objects.get(user=User.objects.get(username=username))
        job_seeker.skill_set = skills
        job_seeker.save()

        return JsonResponse({"message": "successfully inserted!"})

    elif body["action"] == "skills_check":
        username = body["username"]

        user = User.objects.get(username=username)
        job_seeker = JobSeeker.objects.get(user=user)

        return JsonResponse({"skills": job_seeker.skill_set})

    else:
        username = body["username"]
        email = body["email"]
        password = make_password(body["password"])

        user = User.objects.create(username=username, password=password, email=email)
        user.save()

        jobseeker = JobSeeker.objects.create(user=user)
        jobseeker.save()

        return JsonResponse(
            {
                "message": "successfully registered!",
                "user": user.username,
                "isAdmin": user.is_superuser,
            }
        )


@csrf_exempt
def log_in_user(request):
    body = decode_utf(request.body)
    username = body["username"]
    password = body["password"]

    user = User.objects.filter(username=username).first()

    if user is not None:
        if check_password(password, user.password):
            login(request, user)
            return JsonResponse(
                {
                    "message": "user logged in",
                    "user": user.username,
                    "isAdmin": user.is_superuser,
                }
            )
    return JsonResponse({"message": "username or password doesn't match!"})


@csrf_exempt
def log_out_user(request):
    logout(request)

    return JsonResponse({"message": "successfully logged out!"})


@csrf_exempt
def skills(request):
    try:
        body = decode_utf(request.body)
        username = body["username"]

        job_seeker = JobSeeker.objects.get(user=User.objects.get(username=username))
        skills_list = get_skills_from_string(
            skills_string=job_seeker.skill_set, brackets=("[", "]")
        )

        return JsonResponse({"skills": skills_list})
    except Exception:
        skills = set()
        for job in Job.objects.all():
            if job.job_skills:
                skills_list = get_skills_from_string(
                    skills_string=job.job_skills, brackets=("{", "}")
                )
                skills = skills.union(set(skills_list))

        return JsonResponse({"skills": list(skills)})


@csrf_exempt
def recommender(request):
    body = decode_utf(request.body)

    similarity_dict = dict()
    matching_skills_dict = dict()

    skills_list = body["skills"]
    user_skills = set(skills_list)

    user = body["username"]
    filter_dict = body["filter"]

    offset = int(body["offset"])
    n_results = 10

    # try to get from cache
    cache_expired = False
    if body["offset"] != 0:
        try:
            print("getting from cache")
            similarity_dict = json.loads(cache.get(f"{user}_similarity"))
            matching_skills_dict = json.loads(cache.get(f"{user}_matching_skills"))
            if not similarity_dict and not matching_skills_dict:
                raise Exception
        except:
            cache_expired = True
            cache.clear()
    if body["offset"] == 0 or cache_expired:
        for job in Job.objects.filter(
            title__icontains=filter_dict["name"],
            location__icontains=filter_dict["location"],
            qualifications__icontains=filter_dict["qualification"],
            experiences__icontains=filter_dict["experience"],
        ):
            # Salary based filtering
            if not lies_in_salary_range(job.salary, filter_dict["salary"]):
                continue
            # Deadline based filtering
            if not deadline_left(job.deadline, filter_dict["deadline"]):
                continue
            if job.job_skills:
                skills_list = get_skills_from_string(
                    skills_string=job.job_skills, brackets=("{", "}")
                )
                job_skills = set(skills_list)
                (
                    similarity_dict[job.title],
                    matching_skills_dict[job.title],
                ) = jaccard_similarity(job_skills, user_skills)

        similarity_dict = dict(
            sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True)
        )

        cache.set(f"{user}_similarity", json.dumps(similarity_dict), 600)
        cache.set(f"{user}_matching_skills", json.dumps(similarity_dict), 600)

    cache.close()

    @try_and_pass
    def to_send_preparation(i):
        to_sent_dict = dict()
        job = Job.objects.get(title=list(similarity_dict.keys())[i + offset])
        to_sent_dict["title"] = job.title
        to_sent_dict["id"] = job.id
        to_sent_dict["deadline"] = str(job.deadline)
        to_sent_dict["skills"] = job.job_skills
        to_sent_dict["qualification"] = job.qualifications
        to_sent_dict["experience"] = job.experiences
        to_sent_dict["description"] = job.description
        to_sent_dict["salary"] = job.salary
        to_sent_dict["location"] = job.location
        to_sent_dict["level"] = job.level
        to_sent_dict["matching_skills"] = matching_skills_dict[job.title]
        return to_sent_dict

    if similarity_dict.keys():
        result = []
        for i in range(n_results):
            to_sent_dict = to_send_preparation(i)
            if to_sent_dict:
                result.append(json.dumps(to_sent_dict))

        return JsonResponse({"jobs": result})
    return JsonResponse({"jobs": []})


@csrf_exempt
def job(request):
    body = decode_utf(request.body)
    id = body["id"]

    job = Job.objects.get(id=id)
    job_object = {}
    job_object["title"] = job.title
    job_object["deadline"] = job.deadline
    job_object["url"] = job.url
    job_object["skills"] = job.job_skills
    job_object["company_name"] = job.company_name
    job_object["company_info"] = job.company_info
    job_object["company_email"] = job.company_email
    job_object["location"] = job.location
    job_object["description"] = job.description
    job_object["salary"] = job.salary
    job_object["n_vacancy"] = job.n_vacancy
    job_object["level"] = job.level
    job_object["qualification"] = job.qualifications
    job_object["experience"] = job.experiences
    job_object["misc"] = job.misc
    job_object["extracted"] = job.extracted

    return JsonResponse(job_object)


@csrf_exempt
def upload_cv(request):
    username = request.POST["username"]
    fs = FileSystemStorage()
    fs.save(request.FILES["pdf"].name, request.FILES["pdf"])
    pdf_file = open("recommender/uploads/" + request.FILES["pdf"].name, "rb")
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)

    pdf_text = ""
    for i in range(pdf_reader.numPages):
        pdf_text = pdf_text.join(pdf_reader.getPage(i).extractText())
    skills = SkillSet()
    skills.get_skills(pdf_text)
    if not set(skills):
        return JsonResponse(
            {"message": "No skills able to be extracted. So, skillset not saved."}
        )

    job_seeker = JobSeeker.objects.get(user=User.objects.get(username=username))
    job_seeker.skill_set = list(skills)
    job_seeker.save()

    return JsonResponse({"message": "Your skills have been placed in your skillset."})


@csrf_exempt
def logs(request, source):
    body = decode_utf(request.body)
    file = ""
    if source == "log_main":
        file = "main.log"
    elif source == "log_checkjobs":
        file = "checkers/checkjobs.log"
    elif source == "log_interactor":
        file = "interactor/interactor.log"
    elif source == "log_jobdetailsextractor":
        file = "jobdetailsextractor/jobdetailsextractor.log"
    elif source == "log_requestinggoogle":
        file = "requestutils/requestgooglemodule/requestinggoogle.log"

    if body["clear"]:
        if body["clear"] == "all":
            import os

            os.system("./clearlogs.sh")
            return JsonResponse({})
        f = open(file, "w")
        f.close()
        return JsonResponse({})

    with open(file, "r") as log:
        contents = "\n".join(reversed(log.readlines()))
        return JsonResponse({"contents": contents})
