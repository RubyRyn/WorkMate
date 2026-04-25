FROM public.ecr.aws/lambda/python:3.13

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR ${LAMBDA_TASK_ROOT}

# Install into LAMBDA_TASK_ROOT — Lambda's runtime adds it to sys.path
# but does not activate venvs, so `uv sync` into .venv won't work here.
COPY pyproject.toml uv.lock ./
RUN uv export --frozen --no-dev --format requirements-txt -o /tmp/requirements.txt && \
    pip install --no-cache-dir --target ${LAMBDA_TASK_ROOT} -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt pyproject.toml uv.lock

COPY src/                                   ${LAMBDA_TASK_ROOT}/src/
COPY aws_lambda/worker/lambda_function.py   ${LAMBDA_TASK_ROOT}/

CMD ["lambda_function.lambda_handler"]
