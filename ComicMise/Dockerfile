FROM python:3.9-slim

WORKDIR /docker_comicmise

RUN apt-get update && apt-get ins tall -y \
    libpq-dev gcc

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]