FROM python:3.8.7

COPY . /app
WORKDIR /app

ENV POETRY_VERSION="1.1.12"
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/${POETRY_VERSION}/get-poetry.py | python3 -
RUN ln -s /root/.poetry/bin/poetry /usr/local/bin/poetry

RUN poetry install

ENTRYPOINT ["poetry", "run", "python3", "/app/main.py"]
CMD ["--f=1", "--s=1", "--cds=1", "--cl=1"]