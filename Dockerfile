FROM python:3.9.12
ENV ROOT_URL ''
ENV SITE_URL ''
ENV STORAGE_CONNECTION_STRING ''

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
# Set display port as an environment variable
ENV DISPLAY=:99

RUN apt-get update \
    && apt-get -y install gcc make \
    && rm -rf /var/lib/apt/lists/*s

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable
# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Copy files to working directory
WORKDIR /app
COPY ./requirements.txt /app/src/
# Install python packages using requirements.txt
RUN pip install -r src/requirements.txt

COPY ./program.py /app/src/

# Run the script
ENTRYPOINT ["python", "src/program.py"]
