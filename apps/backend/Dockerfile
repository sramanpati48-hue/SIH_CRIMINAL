FROM python:3.10-slim

WORKDIR /app

COPY apps/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/backend/ /app/apps/backend/
COPY packages/shared/ /app/packages/shared/

ENV PYTHONPATH=/app

CMD ["uvicorn", "apps.backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
