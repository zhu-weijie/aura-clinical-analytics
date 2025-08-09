FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./packages/aura_core /app/packages/aura_core
RUN pip install -e ./packages/aura_core

COPY ./src/aura /app/src/aura
COPY pyproject.toml .
RUN pip install .

CMD ["python", "-m", "aura.main"]
