FROM python:3.11

RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    postgresql-client \
    openssl libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /fastapi_app

WORKDIR /fastapi_app

COPY requirements/dev.txt .

RUN pip install -r dev.txt

COPY docker/oauth.py /usr/local/lib/python3.11/site-packages/fastapi_users/router/oauth.py

COPY / .

RUN chmod a+x docker/*.sh
