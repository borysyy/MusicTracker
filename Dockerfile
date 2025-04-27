FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY ./django_project /app/

RUN python manage.py collectstatic

RUN python manage.py migrate

RUN gunicorn myproject.wsgi:application --bind 0.0.0.0:8000



