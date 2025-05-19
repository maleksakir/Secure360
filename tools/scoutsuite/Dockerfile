FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/nccgroup/ScoutSuite.git /opt/ScoutSuite && \
    pip install -r /opt/ScoutSuite/requirements.txt

WORKDIR /opt/ScoutSuite
ENTRYPOINT ["python3", "ScoutSuite.py"]
