git clone https://github.com/advpyt/advanced-python-env.git

cd advanced-python-env

py -3.12 -m venv .venv

.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip

python -m pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser


python manage.py runserver

http://127.0.0.1:8000/

http://127.0.0.1:8000/admin


api

GET http://127.0.0.1:8000/api/books/
