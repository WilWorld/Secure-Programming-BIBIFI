FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user
RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/backend/ /app/
COPY src/frontend/ /app/frontend/

USER appuser
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "app:create_app()"]