from django.http.response import JsonResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from recommender.models import JobSeeker
from jobdetailsextractor.models import Job

import json

# Create your views here.
def register(request):
    if request.POST['action'] == 'username_check':
        username = request.POST['username']
        if User.objects.filter(username=username).first(): return JsonResponse({'message', 'username exists!'})
        else: return JsonResponse({})

    elif request.POST['action'] == 'update':
        username = request.POST['username']
        email = request.POST['email']
        skills = request.POST['skills']
        user = User.objects.get(username=request.COOKIES.get('user'))
        user.username = username
        user.email = email
        user.save()
        jobseeker = JobSeeker.objects.get(user=user)
        jobseeker.skills_set = skills
        jobseeker.save()

        return JsonResponse({'message', 'successfully updated!'})

    elif request.POST['action'] == 'change_password':
        user = User.objects.get(username=request.COOKIES.get('user'))
        password = request.POST['password']
        new_password = request.POST['new_password']
        if not password == user.password: return JsonResponse({'message': 'wrong old password!'})

        user.password = new_password
        user.save()
        return JsonResponse({'message': 'password change successful'})

    else:
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        skills = request.POST['skills']
        user, created = User.objects.get_or_create(
            username=username,
            password=password,
            email=email
        )
        if not created: return JsonResponse({'message': 'user already exists!'})

        user.save()
        jobseeker = JobSeeker.objects.create(user=user, skill_set=skills)
        jobseeker.save()
        return JsonResponse({'message': 'successfully registered!'})

def log_in_user(request):
    username = request.POST['username']
    password = request.POST['password']

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        response = JsonResponse({'message': 'user logged in'})
        response.set_cookie(key='user', value=f'{user.get_username()}', max_age=9999999)
        return response
    else:
        return {'message': "username or password doesn't match!"}

def log_out_user(request):
    logout(request)
    request.COOKIES.delete_cookie('user')
    
    return JsonResponse({'message': 'successfully logged out!'})

def skills(request):
    skills = set()
    for job in Job.objects.all():
        if job.job_skill != 'set()' and job.job_skill:
            skills.union(set(job.job_skill.replace('{', '').replace('}', '').split(',')))
    
    return JsonResponse({'skills': list(skills)})

def recommender(request):
    similarity_dict = dict()
    user_skills = request.POST['skills']
    offset = int(request.POST['offset'])
    n_results = 10
    for job in Job.objects.all():
        job_skills = set(job.job_skills)
        similarity_dict[job.title] = jaccard_similarity(job_skills, user_skills)
        
    similarity_dict = dict(sorted(similarity_dict.items(), key=lambda item: item[1], reverse=True))
    
    result = []
    for i in range(n_results):
        job = Job.objects.get(title=similarity_dict.keys()[i+offset])
        to_sent_dict = dict()
        to_sent_dict['title'] = job.title
        to_sent_dict['deadline'] = job.deadline
        to_sent_dict['skills'] = job.job_skills
        to_sent_dict['qualification'] = job.qualifications
        to_sent_dict['experience'] = job.experiences
        to_sent_dict['description'] = job.description
        to_sent_dict['salary'] = job.salary
        to_sent_dict['location'] = job.location
        to_sent_dict['level'] = job.level
        result.append(json.dumps(to_sent_dict))
    return JsonResponse(json.dumps(result))

def jaccard_similarity(job_skills, candidate_skills):
    if job_skills:
        common_skills = set(job_skills) & set(candidate_skills)
        score = len(common_skills) / len(set(job_skills))
        return score
    else:
        return 0

def job(request):
    title = request.POST['title']
    job = Job.objects.get(title=title)
    job_object = {}
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
    job_object['qualifications'] = job.qualifications
    job_object['experiences'] = job.experiences
    job_object['misc'] = job.misc
    job_object['extracted'] = job.extracted

    return JsonResponse(json.dumps(job_object))