FROM python:3.9.12

ENV FLASK_APP api
ENV STORAGE_CONNECTION_STRING ''

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./static ./static
COPY ./templates ./templates

COPY api.py api.py
COPY startup.py startup.py

EXPOSE 80

CMD [ "python3", "-u", "-m" , "gunicorn", "--bind=0.0.0.0:80", "startup:app"]