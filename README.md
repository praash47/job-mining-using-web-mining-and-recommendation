# Job Mining in Non AJAX Based Nepali Websites using Web Mining and Recommending Users
Welcome to our fourth year project repo! We are a group of four enthusiastic friends:
* Aashish Tamrakar
* Asim Aryal
* Niroj Bajracharya
* Sudip Gyawali

currently studying fourth year at [National College of Engineering](https://nce.edu.np).

## Our starting emotions for the project (March 5, 2021)
This project is not just our college project. This project dedicated for future will be our emotion.

Anticipated to be grand, full of positive emotions to contribute in the name of computer science, in the name of our country, to make the world; a better place to live in is expected in this project. 

This project is to be with full of dedications, selfless contributions and hard work! Not caring about time, nor ourselves, we have to give our 100, no 120% efforts for this and make something valuable out of it. Not to satisfy anyone, not to show anyone, not to express anything to anyone, this project should consist efforts the best.

## Installation
The installation of this project is a bit long and tedious. But, you can stick along with us and perform each step with care step by step. Just remember, we had 1000s of this types of commands run before this project started completely running. There may be some issues while in installation. Try to fix it yourself by googling the error (because there may be complex unaniticipated issues) or you can feel free to ask to us.

### Steps
#### Required Programs and Dependent Softwares & Databases
1. Install Chrome on your machine from [here](https://www.google.com/chrome/). (Required for `selenium`)
2. Download `Python 3.8.10` from [here](https://www.python.org/downloads/release/python-3810/) (Tested in `python 3.8.10`). Be sure that you are using `python 3.8.10` the whole time.
3. Download `Postgresql` from [here](https://www.postgresql.org/download/windows/).
4. Download your appropriate version of `Chromedriver` from [here](https://chromedriver.chromium.org/) and place it inside `jobminersserver/searcher/Yoqs/` and name it `chromedriver`. You can find the appropriate version number inside about section of Chrome.

#### Database Setup
5. Open `Pgadmin 4`, Choose a master password and make sure you remember the password.
6. **Creation of Admin and Assigning Privileges:** Under Server open `PostgreSQL <version_num>` > Login/Group Roles, Add username `jobminer` and password `jobminer`. Go into properties of user `jobminer`, then check all the boxes under Privileges tab.
7. Create a server named `jobminer`, Type localhost in Host name/address, supply master password in password.
8. Under Databases of `jobminer`, create a database named `jobminers` (notice **s**), set Owner to `jobminer`.

#### Virtual Environment Creation and Python Dependencies Installation
9. Go to jobminersserver folder in your files, Run `setup.bat` if you are in windows and `setup.sh` if you are in linux. This basically creates a virtual environment into `.env` and installs all the dependencies mentioned in `requirements.txt`. If it is not able to do it automatically, then you have to run each line of code inside the `setup.bat`.
10. This prompt also creates tables in the database and prompt should ask username, email and password, enter `jobminer`, `jobminer@jobminer.com` and `jobminer`, then after that type `y` ignoring the warnings.
11. `Stopwords`, `wordnet`, and `punkt` is also downloaded automatically which are libraries in python's Natural Language Processing Toolkit.

#### Running the server
12. Go into `jobminersserver/jobdetailsextractor/apps.py` and remove comment from `def ready():` to end of file. This enables our `timers` module which is responsible for our jobs extraction.
13. Open command prompt/shell in `jobminersserver` folder and run:
```
source .env/bin/activate # linux
# windows
cd .env/Scripts/
activate
cd ../../
# then:
python manage.py runserver --noreload
```
13. Go into http://localhost:8000 and register an account and enjoy the job recommendations and you can also see the server mining in `Backend Daemon` of the website.
14. Note the following things:
- You won't have any jobs at first, because the job miner needs to find out the job websites and find the current jobs in it and start extracting.
- Each extraction takes at the rate of default of `5 mins` per job and cycles through the available job websites.
- You can change the extraction time in mins in  `jobminersserver/timers/timersettings.ini`. **_Extremely Important thing: Don't set it to too low, i.e. less than 1 minute because, sending too many requests to a web server in a short period of time is ILLEGAL AND UNETHICAL, this is the reason while we introduced the timers module at the first place, for requesting each website ethically and on a timely basis._**

## Documentations
### Code
Code Documentations are also found inline for most of the code in form of inline comments and docstrings. If you prefer to visit a documentation form of site then, it is temporarily available at [here](https://job-mining-docs.000webhostapp.com/).
### Reports and Slides
Please request us for the report and slides.

Have a good day & yeah, `Keep Mining`!.
