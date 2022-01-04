from django.http.response import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from recommender.models import JobSeeker
from jobdetailsextractor.models import Job

from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

import json

@csrf_exempt
def register(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    if body['action'] == 'username_check':
        username = body['username']
        if User.objects.filter(username=username).first(): 
            return JsonResponse({'message': 'username exists!',})
        else: return JsonResponse({})

    elif body['action'] == 'email_needed':
        username = body['username']
        return JsonResponse({'email': User.objects.get(username=username).email})

    elif body['action'] == 'update':
        ousername = body['ousername']
        username = body['username']
        email = body['email']
        skills = body['skills']
        user = User.objects.get(username=ousername)
        user.username = username
        user.email = email
        user.save()
        jobseeker = JobSeeker.objects.get(user=user)
        jobseeker.skill_set = skills
        jobseeker.save()

        return JsonResponse({
            'message': 'successfully updated!',
            'user': user.username
        })

    elif body['action'] == 'change_password':
        username = body['username']
        user = User.objects.get(username=username)
        password = body['password']
        new_password = make_password(body['new_password'])
        if check_password(password, user.password):
            user.password = new_password
            user.save()
            return JsonResponse({'message': 'password change successful'})
        else: return JsonResponse({'message': 'wrong old password!'})

    elif body['action'] == 'skills_insert':
        skills = body['skills']
        username = body['username']
        job_seeker = JobSeeker.objects.get(user=User.objects.get(username=username))
        job_seeker.skill_set = skills
        job_seeker.save()

        return JsonResponse({'message': 'successfully inserted!'})

    elif body['action'] == 'skills_check':
        username = body['username']
    
        user = User.objects.get(username=username)
        job_seeker = JobSeeker.objects.get(user=user)
        
        return JsonResponse({'skills': job_seeker.skill_set}) 

    else:
        username = body['username']
        email = body['email']
        password = make_password(body['password'])
        user= User.objects.create(
        username=username,
        password=password,
        email=email
        )

        user.save()
        jobseeker = JobSeeker.objects.create(user=user)
        jobseeker.save()
        return JsonResponse({
            'message': 'successfully registered!',
            'user': user.username,
        })

@csrf_exempt
def log_in_user(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    username = body['username']
    password = body['password']

    user = User.objects.filter(username=username).first()

    if user is not None:
        if check_password(password, user.password):
            login(request, user)
            return JsonResponse({
                'message': 'user logged in',
                'user': user.username
            })
    return JsonResponse({'message': "username or password doesn't match!"})

@csrf_exempt
def log_out_user(request):
    logout(request)
        
    return JsonResponse({'message': 'successfully logged out!'})

@csrf_exempt
def skills(request):
    try:
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        job_seeker = JobSeeker.objects.get(user=User.objects.get(username=username))
        skills_list = job_seeker.skill_set.replace('[', '').replace(']', '')
        skills_list = skills_list.replace(', ', ',').replace("'", "").split(',')
        return JsonResponse({'skills': skills_list})
    except Exception:
        skills = set()
        for job in Job.objects.all():
            if job.job_skills:
                skills_list = job.job_skills.replace('{', '').replace('}', '')
                skills_list = skills_list.replace(', ', ',').replace("'", "").split(',')
                skills = skills.union(set(skills_list))
        return JsonResponse({'skills': list(skills)})

@csrf_exempt
def recommender(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    similarity_dict = dict()
    matching_skills_dict = dict()
    skills_list = body['skills']
    user_skills = set(skills_list)
    offset = int(body['offset'])
    n_results = 10
    for job in Job.objects.all():
        if job.job_skills:
            skills_list = job.job_skills.replace('{', '').replace('}', '')
            skills_list = skills_list.replace(', ', ',').replace("'", "").split(',')
            job_skills = set(skills_list)
            similarity_dict[job.title], matching_skills_dict[job.title] = \
                jaccard_similarity(job_skills, user_skills)

    similarity_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))
    print(similarity_dict)
    result = []
    for i in range(n_results):
        try:
            to_sent_dict = dict()
            job = Job.objects.get(title=list(similarity_dict.keys())[i+offset])
            to_sent_dict['title'] = job.title
            to_sent_dict['id'] = job.id
            to_sent_dict['deadline'] = job.deadline
            to_sent_dict['skills'] = job.job_skills
            to_sent_dict['qualification'] = job.qualifications
            to_sent_dict['experience'] = job.experiences
            to_sent_dict['description'] = job.description
            to_sent_dict['salary'] = job.salary
            to_sent_dict['location'] = job.location
            to_sent_dict['level'] = job.level
            to_sent_dict['matching_skills'] = matching_skills_dict[job.title]
            result.append(json.dumps(to_sent_dict))
        except: pass
    return JsonResponse({'jobs': result})

def jaccard_similarity(job_skills, candidate_skills):
    if job_skills:
        common_skills = set(job_skills) & set(candidate_skills)
        score = len(common_skills) / len(set(job_skills))
        return score, list(common_skills)
    else:
        return 0, []

@csrf_exempt
def job(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    id = body['id']
    job = Job.objects.get(id=id)
    job_object = {}
    job_object['title'] = job.title
    job_object['deadline'] = job.deadline
    job_object['url'] = job.url
    job_object['skills'] = job.job_skills
    job_object['company_name'] = job.company_name
    job_object['company_info'] = job.company_info
    job_object['company_email'] = job.company_email
    job_object['location'] = job.location
    job_object['description'] = job.description
    job_object['salary'] = job.salary
    job_object['n_vacancy'] = job.n_vacancy
    job_object['level'] = job.level
    job_object['qualification'] = job.qualifications
    job_object['experience'] = job.experiences
    job_object['misc'] = job.misc
    job_object['extracted'] = job.extracted

    return JsonResponse(job_object)
