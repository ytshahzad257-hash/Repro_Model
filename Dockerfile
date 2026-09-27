FROM python:3.12.3-slim
WORKDIR /artifact
COPY . /artifact
RUN pip install --no-cache-dir -e .
CMD ["python", "experiments/run_all.py", "--fast"]
