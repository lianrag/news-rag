FROM python:3.11

WORKDIR /app

COPY .env ./
COPY api/ ./api/
COPY ui/ ./ui/

RUN pip install --upgrade pip
RUN pip install -r api/requirements.txt && pip install -r ui/requirements.txt

CMD ["bash"]
