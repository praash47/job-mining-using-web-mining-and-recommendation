pip install virtualenv
virtualenv .env
cd .env/Scripts/
activate
cd ../../
pip install setuptools==45.2.0
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python nltk-downloads.py