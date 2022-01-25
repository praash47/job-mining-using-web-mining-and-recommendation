import pandas as pd
from nltk.util import ngrams
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

class SkillSet():
    def __init__(self):
        skills = pd.read_csv("/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/jobdetailsextractor/all_skills.csv")
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
        skills = self.skill_words['1 gram'].union(self.skill_words['2 grams'])
        skills = skills.union(self.skill_words['3 grams']).union(self.skill_words['4 grams'])
        skills = skills.union(self.skill_words['5 grams'])
        return (skill for skill in skills)

    def get_skills(self, skills_text):
        lemmatized = self.lemmatizer.lemmatize(skills_text.lower())
        word_tokens = word_tokenize(lemmatized)

        tokens = [w for w in word_tokens if not w.lower() in self.stop_words \
             and not w == '.' and not w == ',' and not w == '?']

        output_2grams = [' '.join(tup) for tup in list(ngrams(tokens, 2))]
        output_3grams = [' '.join(tup) for tup in list(ngrams(tokens, 3))]
        output_4grams = [' '.join(tup) for tup in list(ngrams(tokens, 4))]
        output_5grams = [' '.join(tup) for tup in list(ngrams(tokens, 5))]
        self.skill_words['1 gram'] = self.all_skills & set(tokens)
        self.skill_words['2 grams'] = self.all_skills & set(output_2grams)
        self.skill_words['3 grams'] = self.all_skills & set(output_3grams)
        self.skill_words['4 grams'] = self.all_skills & set(output_4grams)
        self.skill_words['5 grams'] = self.all_skills & set(output_5grams)

        self.filter_lower_grams()

    def filter_lower_grams(self):
        grams = list(self.skill_words.keys())
        grams.reverse()
        for gram in grams:
            if not self.skill_words[gram]: continue
            else:
                later_gram = str(int(gram[0])-1) + ' gram'
                try: 
                    if int(gram[0]) - 1 > 1: later_gram += 's'
                    one_gram_present_in_two = []
                    for higher_gram in self.skill_words[gram]:
                        one_gram_present_in_two = [skill for skill in self.skill_words[later_gram] if skill in higher_gram]
                    for skill in one_gram_present_in_two:
                        self.skill_words[later_gram].remove(skill)
                except: pass

if __name__ == "__main__":
    skillset = SkillSet()
    skills_text = '''Other Specification
Qualifications Required 

University Bachelor's degree in Computer Engineering or equivalent in relevant stream 
Minimum 2 years of professional work experience in software development 
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
Should have sound analytical skills and problem-solving skills
Job Description
Position Overview 

Are you passionate about developing state-of-the-art digital solutions? Do you want to work with the award-winning Development team? 

We are looking for top-notch ReactJS or VueJS Developers who will be responsible members of the Web application / Mobile app team at EB Pearls. This position is responsible for developing projects as per clients’ requirements. NodeJs developer reports directly to the Project Manager and is accountable for the Project Development. 

Job Roles and Responsibilities: 

1. Project Accountability 

Understand the project requirements clearly. 
Generate queries in case there is any confusion in understanding the project.
Discuss any technical challenges that might come affront while working on the project.
Realize the project delivery date and understand the communication channels. 
Write codes to develop a quality product on time. 
Conduct first-hand testing of the project tasks before submitting the tasks to the Project Manager. 
Verify the product with SRS. 
2. Adapt to EB Work Culture 

Attend project meetings conducted by the Project Manager with full preparation by studying the project documents and information. 
Follow company coding standards. 
3. Team Coordination 

Take ownership of the project from planning to the delivery of the project. 
Be easily approachable and flexible in work. 
Perks and Benefits 

We strive to make sure that our people are comfortable, happy, and growing at EB Pearls. We offer: 

Insurance: We enroll our employees in the company's group insurance policy that covers both medical and accidental insurance. 
Competitive Salary: We strive to ensure that our people get competitive remuneration as per the industry standards 
Timely performance appraisal and salary reviews: We conduct bi-yearly performance reviews to ensure that our people are always on top of their game and ensure yearly salary reviews on a timely basis to complement. 
Paid Time Off (PTO)/ Paid Holidays: PTO refers to days when you can take time away from work while still being paid your usual salary. We provide 13 business days off as festival holidays. 
Employee Recognition: We are a company led by performers and we never fail to acknowledge the exemplary performance of our people 
Social Security Fund: SSF is a contribution-based social security scheme, the employee contributes 11 % and the employer adds 20% of the basic salary per month( 31% of the basic salary of employee) every month. 
Festival Allowance: We have the provision of festival allowance and provide Dashain bonus which is based on the amount of employees’ basic salary. 
Training and Development Programs: We are obsessed with constantly developing our competencies. Hence, we determine the training needs for our people from the performance review that we conduct bi- yearly. 
Work on next-generation technology projects
Work with leading edge technology 
Fun At EB 

All work and no play is not our cup of tea. At EB, we enjoy: 

Office Events: Chat and Chew, Residential Annual Event, Team Lunch Out 
EEC Club Activities : Night outs, Picnics, Lunch Outs, Futsal, Festival Events, Pool Parties, Day out events 
Food and Coffee: Office Provided lunch and stocked pantry 
Inspiring Colleagues: Fun and friendly work environment with brilliant one of a kind team 
Applying Procedure: 

Submit a cover letter along with your recently updated resume via email to “careers@ebpearls.com” with “ReactJS/VueJS Developer” in the subject line. 

OR, 

Send your application via our website: CLICK HERE

OR,'''
    skillset.get_skills(skills_text)
    print(set(skillset))