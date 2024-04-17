#!/bin/bash

echo 'export TF_ENABLE_ONEDNN_OPTS=0' >> ~/.bashrc

source ~/.bashrc

sleep 5

alembic upgrade head

cd src

#gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
