"""
Utilities reqeuired for the views, or in dealing with the client.
"""
import json
import re

from datetime import datetime
from decimal import Decimal
from math import floor
from re import sub

from django.utils import timezone

def decode_utf(body):
    """
    Decodes the UTF text to a dict format and returns it.
    A request.POST could be used instead.

    Parameters
    ----------
    body: request.body
        body of the request
    
    Returns
    -------
    dict
        Dict of the body.
    """
    body_unicode = body.decode('utf-8')
    return json.loads(body_unicode)

def jaccard_similarity(job_skills, candidate_skills):
    """
    Computes and returns the Jaccard similarity between two skillsets namely job skills and candidate skills. Returns score and common skills.

    Parameters
    ----------
    job_skills: list
        List of job skills
    candidate_skills: list
        List of candidate skills

    Returns
    -------
    float, list
        score and list of common skills if job_skills available, else, 0 and []
    """
    if job_skills:
        common_skills = set(job_skills) & set(candidate_skills)
        score = len(common_skills) / \
            len(set(job_skills).union(set(candidate_skills)))
        return score, list(common_skills)
    else:
        return 0, []

def get_skills_from_string(skills_string, brackets):
    """
    From a skill set, remove brackets and parse out the skills into a list.

    Parameters
    ----------
    skills_string: str
        string where the skills are present
    brackets: tuple
        opening and closing brackets from which to parse.

    Returns
    -------
    list
        List of the skills
    """
    skills_list = skills_string.replace(brackets[0], '').replace(brackets[1], '')
    return skills_list.replace(', ', ',').replace("'", "").split(',')

def lies_in_salary_range(job_salary, salary):
    if (job_salary and (salary['lower'] or salary['upper'])):
        if (job_salary == 'negotiable'): return False
        salaries_range = [Decimal(sub(r'[^\d.]', '', salary)) for salary in job_salary.split(' ') if re.search(r'\d', salary)]

        n_salaries = len(salaries_range) - 1
        if (salary['lower'] and salary['upper'] \
        and salary['upper'] > salary['lower'] \
        and salary['lower'] >= salaries_range[0] \
        and salary['upper'] <= salaries_range[n_salaries]): return True
        elif salary['lower']:
            if salaries_range[0] >= salary['lower'] \
                and salary['lower'] <= salaries_range[n_salaries] \
                and not salary['upper']: return True
        elif salary['upper']:
            if not salary['lower'] \
                and salaries_range[n_salaries] <= salary['upper']: return True
            
        return False
    return True

def deadline_left(job_deadline, deadline):
    if job_deadline and (deadline['days'] or deadline['months']):
        if job_deadline == 'Not Available': return False
        days, months = get_deadline(job_deadline)
        
        if deadline['days'] == 0: return deadline['months'] <= months
        if deadline['months'] == 0: return deadline['days'] <= days

        if not deadline['days']: deadline['days'] = 0
        if not deadline['months']: deadline['months'] = 0

        if deadline['days'] <= days \
        and deadline['months'] <= months: return True

        return False
    return True

def get_deadline(date):
    if date:
        deadline_date = date
        now = timezone.now()
        if (now > deadline_date): return False, False

        diff = abs(now - deadline_date)

        days = diff.days
        months = floor(days / 30)
        days = floor(days % 30) if months > 0 else days

        return days, months
    return None, None   