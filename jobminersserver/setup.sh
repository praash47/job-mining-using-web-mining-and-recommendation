pip install virtualenv
python3 -m venv .env
source .env/bin/activate
pip install setuptools==45.2.0
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py createsuperuser
python3 nltk-downloads.py