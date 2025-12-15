
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY back/ ./back/

RUN playwright install chromium

ENV PYTHONUNBUFFERED=1
CMD ["pytest", "back/test/", "-v", "--tb=short"]