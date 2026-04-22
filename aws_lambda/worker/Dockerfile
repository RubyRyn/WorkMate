FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Install core dependencies directly to avoid build issues
RUN pip install langchain-text-splitters==0.0.1 chromadb==0.4.24 google-genai==0.3.0 boto3==1.34.14 requests==2.31.0 urllib3==1.26.18

# Copy application source
COPY src/ ./src/
COPY aws_lambda/worker/lambda_function.py ./

CMD ["lambda_function.lambda_handler"]
