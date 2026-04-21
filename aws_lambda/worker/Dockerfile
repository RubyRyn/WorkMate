FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Install core dependencies directly to avoid build issues
RUN pip install langchain-text-splitters chromadb google-genai boto3 requests urllib3

# Copy application source
COPY src/ ./src/
COPY aws_lambda/worker/lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
