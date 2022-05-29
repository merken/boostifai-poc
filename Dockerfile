FROM python:3.9.12
ARG root_url
ARG site_url
ARG STORAGE_CONNECTION_STRING
# Update base packages
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get -y install gcc
# Adding trusting keys to apt for repositories
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

# Adding Google Chrome to the repositories
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

# Updating apt to see and install Google Chrome
RUN apt-get -y update

# Magic happens
RUN apt-get install -y google-chrome-stable

# Installing Unzip
RUN apt-get install -yqq unzip

# Download the Chrome Driver
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/102.0.5005.61/chromedriver_linux64.zip

# Unzip the Chrome Driver into /usr/local/bin directory
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# Set display port as an environment variable
ENV DISPLAY=:99

# Change TimeZone
ENV TZ=Europe/Brussels
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
RUN echo $(date)

# Copy files to working directory
WORKDIR /app
COPY ./requirements.txt /app/src/
# Install python packages using requirements.txt
RUN pip install -r src/requirements.txt

COPY ./program.py /app/src/
# Run the script
ENTRYPOINT ["python", "src/program.py"]
