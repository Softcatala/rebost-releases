FROM python:3.14-slim AS base

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
# the log is written as things happen, not when the buffer fills up
ENV PYTHONUNBUFFERED=1


FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM python-deps AS tests

RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy --dev

COPY . .
RUN pipenv run pytest tests/
RUN touch /tmp/tests

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"


COPY --from=tests /tmp/tests /tmp/

# Create and switch to a new user
RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

# Install application into container
COPY . .

EXPOSE 5000

# Run the application, as gunicorn.conf.py says
ENTRYPOINT ["gunicorn", "handler:app"]
