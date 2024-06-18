# Use Python 3.11-bookworm as the base image
FROM python:3.11-bookworm

# Install system dependencies
RUN apt-get update \
    && apt-get install -y \
        curl \
        wget \
        gnupg \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set the timezone to Europe/Berlin
RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata

# Install Chromedriver
ENV ChromedriverVersion="126.0.6478.55"
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$ChromedriverVersion/linux64/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Set the display port to avoid crashes
ENV DISPLAY=:99

# Set environment variables
ENV OCTIV_USERNAME=""
ENV OCTIV_PASSWORD=""
ENV EMAIL_SENDER=""
ENV EMAIL_PASSWORD=""
ENV EMAIL_RECEIVER=""
ENV DAYS_BEFORE_BOOKABLE=""
ENV EXECUTION_BOOKING_TIME=""

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /root/workspaces
