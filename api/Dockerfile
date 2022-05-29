FROM python:3.9

ENV FLASK_APP api
ENV STORAGE_CONNECTION_STRING ''

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ./static ./static
COPY ./templates ./templates

COPY api.py api.py

CMD [ "python3", "-u", "-m" , "gunicorn", "run", "--host=0.0.0.0"]