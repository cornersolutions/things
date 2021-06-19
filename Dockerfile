# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8.3-slim-buster as base

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt
ENV FLASK_APP=server.py

COPY ./src/ /src
WORKDIR /src

FROM base as debug
RUN pip install ptvsd
WORKDIR /src
CMD python -m ptvsd --host 0.0.0.0 --port 5678 --wait --multiprocess -m flask run -h 0.0.0 -p 8080

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
#CMD ["gunicorn", "--bind", "0.0.0.0:8080", "src\app:app"]
