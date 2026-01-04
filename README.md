git clone https://github.com/advpyt/advanced-python-env.git
cd advanced-python-env

python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
