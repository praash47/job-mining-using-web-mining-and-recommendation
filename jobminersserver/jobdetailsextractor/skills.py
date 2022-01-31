"""
This submodule extracts out skillset from the given text. This submodule compares with our skills in all_skills.csv.

Classes
-------
SkillSet()
    Skill set of something, maybe job or user
"""
import logging

import pandas as pd

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

mainlogger = logging.getLogger('main')
logger = logging.getLogger('jobdetailsextractor')


class SkillSet():
    """
    Skill set of a user or job

    Methods
    -------
    get_skills(skills_text)
        Get skills from giver skills_text
    iter(skills_object): Eg. set(skills_object)
        Get the skills as the desired iterable. set in the case of example
    """

    def __init__(self):
        """
        Skill set of a user or job.

        Instructions
        ------------
        * Use get_skills(skills_text) to get skills
        * Then, using set or list or any iterable as set(skills_object).
        """
        mainlogger.info('SkillSet Object Created')
        logger.info('SkillSet Object Created')
        skills = pd.read_csv("jobdetailsextractor/reqs/all_skills.csv")
        self.all_skills = set(skills['skill'])
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

        self.skill_words = {
            "1 gram": {},
            "2 grams": {},
            "3 grams": {},
            "4 grams": {},
            "5 grams": {}
        }

    def __iter__(self):
        """
        Returns an iterable of the skills set.

        Usage
        -----
        set(skills_object) where skills_object is the object of which to get set of skills out of.

        Note: Run this only after running get_skills()

        Returns
        -------
        iterable
            iterable of the skills
        """
        # Union all the gram skills and return
        skills = self.skill_words['1 gram'].union(self.skill_words['2 grams'])
        skills = skills.union(self.skill_words['3 grams']).union(
            self.skill_words['4 grams'])
        skills = skills.union(self.skill_words['5 grams'])
        logger.info(skill for skill in skills)
        return (skill for skill in skills)

    def get_skills(self, skills_text):
        """
        Gets skills from the skills_text and store it into 1-5 grams internal variable.
        """
        # lemmatize the text
        lemmatized = self.lemmatizer.lemmatize(skills_text.lower())
        # tokenize the text
        word_tokens = word_tokenize(lemmatized)

        # remove . , and ?
        tokens = [w for w in word_tokens if not w.lower() in self.stop_words
                  and not w == '.' and not w == ',' and not w == '?']

        # find n grams
        output_2grams = [' '.join(tup) for tup in list(ngrams(tokens, 2))]
        output_3grams = [' '.join(tup) for tup in list(ngrams(tokens, 3))]
        output_4grams = [' '.join(tup) for tup in list(ngrams(tokens, 4))]
        output_5grams = [' '.join(tup) for tup in list(ngrams(tokens, 5))]

        # find common between all skills and the n grams and store in equivalent skill_words.
        self.skill_words['1 gram'] = self.all_skills & set(tokens)
        self.skill_words['2 grams'] = self.all_skills & set(output_2grams)
        self.skill_words['3 grams'] = self.all_skills & set(output_3grams)
        self.skill_words['4 grams'] = self.all_skills & set(output_4grams)
        self.skill_words['5 grams'] = self.all_skills & set(output_5grams)

        # Filter out lower grams.
        self.filter_lower_grams()

    def filter_lower_grams(self):
        """
        Filters out lower grams from the obtain skills. For eg.: Web Application Services is prioritized, and Application Services or Web Application is filtered out.
        """
        grams = list(self.skill_words.keys())
        grams.reverse()
        for gram in grams:
            # If gram that doesn't exist arrives.
            if not self.skill_words[gram]:
                continue
            else:
                later_gram = str(int(gram[0])-1) + ' gram'
                try:
                    # for more than 1 gram enter s for indexing
                    if int(gram[0]) - 1 > 1:
                        later_gram += 's'
                    one_gram_present_in_two = []
                    # Find a lower gram that is present in the higher gram.
                    for higher_gram in self.skill_words[gram]:
                        one_gram_present_in_two = [
                            skill for skill in self.skill_words[later_gram] if skill in higher_gram]
                    # Remove all the lower grams.
                    for skill in one_gram_present_in_two:
                        self.skill_words[later_gram].remove(skill)
                except:
                    pass


if __name__ == "__main__":
    skillset = SkillSet()
    skills_text = '''
    Skills Required 

    Strong knowledge in javascript
    Proficient in developing web applications
    Must have experience in web application development using VueJs or ReactJS
    Sound knowledge in working with restful API or GraphQL
    Proficient in understanding of code versioning tools, such as Git
    Good knowledge of SQL and No-SQL 
    Good knowledge of HTML and CSS (SCSS or similar) 
    
    Skills Preferred 

    Experience in developing applications using MEARN stack 
    Proficient in understanding of CI/CD pipeline
    Understanding differences between multiple delivery platforms, such as mobile vs. desktop, and optimizing output to match the specific platform
    Sound knowledge in unit testing
    Should have sound analytical skills and problem-solving skills'''
    skillset.get_skills(skills_text)
    print(set(skillset))
