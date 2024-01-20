#!/bin/bash

echo 'export TF_ENABLE_ONEDNN_OPTS=0' >> ~/.bashrc

source ~/.bashrc

sleep 5

alembic upgrade head

cd src

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000