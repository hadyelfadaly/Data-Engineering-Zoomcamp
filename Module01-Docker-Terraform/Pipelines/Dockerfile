FROM python:3.13.11-slim

RUN pip install pandas pyarrow

WORKDIR /app
COPY pipeline.py pipeline.py

ENTRYPOINT ["python", "pipeline.py"]