FROM python:3.8

RUN pip install pipenv

COPY ./Pipfile ./Pipfile
COPY ./Pipfile.lock /Pipfile.lock

RUN pipenv install --deploy --system --ignore-pipfile

COPY service-account.json .

COPY ./daily_word_bot ./daily_word_bot


EXPOSE 8443

RUN echo python -V

CMD [ "python", "-m", "daily_word_bot"]
