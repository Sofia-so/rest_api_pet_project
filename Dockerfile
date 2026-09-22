FROM python:3.12-slim

EXPOSE 5000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /src

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "gunicorn --bind 0.0.0.0.:$PORT 'app:create_app()'"]
