FROM python:3.10

# install google chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# SET TIMEZONE
RUN apt update && apt install tzdata -y
ENV TZ="Europe/Berlin"

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# arg directivy to pass at build-time
ARG OCTIV_USERNAME=${OCTIV_USERNAME:-""}
# set environment variables
ENV OCTIV_USERNAME=${OCTIV_USERNAME}

ARG OCTIV_PASSWORD=${OCTIV_PASSWORD:-""}
ENV OCTIV_PASSWORD=${OCTIV_PASSWORD}


RUN mkdir /app
COPY slotbooker/* /app/


COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN chmod 644 $(find /app/. -type f)
RUN chmod 755 $(find /app/. -type d)

#ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install -Ur requirements.txt

RUN pip3 install webdriver-manager

#RUN pip3 install poetry
#RUN poetry config virtualenvs.create false
#RUN poetry install
# RUN poetry install --no-dev

ENTRYPOINT [ "python", "booker.py" ]
