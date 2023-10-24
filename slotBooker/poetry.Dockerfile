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
# currently not working as chromedriver only has 114 and chrome is 116
# RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
# RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# https://googlechromelabs.github.io/chrome-for-testing/#stable
RUN wget -O /tmp/chromedriver.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/118.0.5993.70/linux64/chromedriver-linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver-linux64/chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

# arg directivy to pass at build-time
ARG OCTIV_USERNAME=${OCTIV_USERNAME:-""}
ARG OCTIV_PASSWORD=${OCTIV_PASSWORD:-""}
ARG EMAIL_SENDER=${EMAIL_SENDER:-""}
ARG EMAIL_PASSWORD=${EMAIL_PASSWORD:-""}
ARG EMAIL_RECEIVER=${EMAIL_RECEIVER:-""}
ARG DAYS_BEFORE_BOOKABLE=${DAYS_BEFORE_BOOKABLE:-""}
ARG EXECUTION_BOOKING_TIME=${EXECUTION_BOOKING_TIME:-""}
# set environment variables
ENV OCTIV_USERNAME=${OCTIV_USERNAME}
ENV OCTIV_PASSWORD=${OCTIV_PASSWORD}
ENV EMAIL_SENDER=${EMAIL_SENDER}
ENV EMAIL_PASSWORD=${EMAIL_PASSWORD}
ENV EMAIL_RECEIVER=${EMAIL_RECEIVER}
ENV DAYS_BEFORE_BOOKABLE=${DAYS_BEFORE_BOOKABLE}
ENV EXECUTION_BOOKING_TIME=${EXECUTION_BOOKING_TIME}

RUN mkdir /app
COPY ./slotBooker /app
COPY ./slotBooker/pyproject.toml /app

WORKDIR /app

# make files executable
#RUN chmod 644 $(find . -type f)
#RUN chmod 755 $(find . -type d)

ENV PYTHONPATH=${PYTHONPATH}:${PWD}

RUN pip3 install poetry
RUN poetry config virtualenvs.create false && poetry install
# RUN poetry install --no-dev
# RUN poetry install

ENTRYPOINT [ "poetry", "run", "slotBooker" ]
