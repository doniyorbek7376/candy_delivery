@echo off
cd env/Scripts && ^
activate.bat && ^
cd ../.. && ^
python manage.py test