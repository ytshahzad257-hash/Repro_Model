FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends openjdk-17-jre-headless curl git procps && rm -rf /var/lib/apt/lists/*
WORKDIR /artifact
COPY . /artifact
RUN pip install --no-cache-dir -e '.[dev]' \
 && curl --fail --location --output /opt/tla2tools.jar https://github.com/tlaplus/tlaplus/releases/download/v1.8.0/tla2tools.jar \
 && python -c "import hashlib; assert hashlib.sha256(open('/opt/tla2tools.jar','rb').read()).hexdigest() == '15d103b7e5617780bcc904c0af12f1ad242e2b345c0301136c5be4588f17edac'"
ENV TLA2TOOLS_JAR=/opt/tla2tools.jar
ENV JAVA_TOOL_OPTIONS=-Xmx2g
# Explicit stub/reuse mode; this image does not claim fresh local-model inference.
CMD ["python", "experiments/run_all.py", "--dry-run", "--jobs", "2"]
