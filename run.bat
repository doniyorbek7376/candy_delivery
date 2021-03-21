@echo off
cd env/Scripts && ^
activate.bat && ^
cd ../.. && ^
python manage.py runserver 0.0.0.0:8000