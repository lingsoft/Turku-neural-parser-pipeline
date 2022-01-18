#!/bin/sh
# now fetch the model
# /sbin/tini -s -- venv/bin/python fetch_models.py $MODEL && 
exec /sbin/tini  -- venv/bin/gunicorn --bind=0.0.0.0:8000 "--workers=$WORKERS" "--timeout=$TIMEOUT" "--worker-class=$WORKER_CLASS" --worker-tmp-dir=/dev/shm "$@" tnpp_serve_elg:app
