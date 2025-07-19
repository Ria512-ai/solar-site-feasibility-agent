FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV NEWS_API_TOKEN=""
ENV OPENAI_API_KEY=""

CMD ["python", "main.py"]