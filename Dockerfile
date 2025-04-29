FROM python:3.13

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./django_project /app/

COPY ./static/default/default-profile.jpg ./media/profile_pictures/

COPY ./static/default/default.jpg ./media/collection_thumbnails/
