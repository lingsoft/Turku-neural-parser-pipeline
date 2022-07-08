# Build venv
FROM python:3.8 as venv-build
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt fetch_models.py /app/
RUN pip install --no-cache-dir -r requirements.txt && python fetch_models.py fi_tdt_dia

# Install basic deps
FROM python:3.8-slim
WORKDIR /elg

RUN apt-get update && apt-get -y install --no-install-recommends tini vim \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/* && chmod +x /usr/bin/tini

COPY  --from=venv-build /opt/venv /opt/venv
COPY  --from=venv-build /app/models_fi_tdt_dia /elg/models_fi_tdt_dia
COPY  --from=venv-build /app/TurkuNLP/bert-base-finnish-cased-v1 /elg/TurkuNLP/bert-base-finnish-cased-v1
COPY  tnparser /elg/tnparser
COPY  app.py docker-entrypoint.sh /elg/
COPY  utils /elg/utils
COPY tests /elg/tests

ENV PATH="/opt/venv/bin:$PATH"
ENV WORKERS=2
ENV TIMEOUT=360
ENV WORKER_CLASS=sync
ENV LOGURU_LEVEL=INFO
ENV PYTHON_PATH="/opt/venv/bin"
RUN chmod +x /elg/docker-entrypoint.sh
ENTRYPOINT ["/elg/docker-entrypoint.sh"]