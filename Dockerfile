# syntax=docker/dockerfile:1
FROM python:3.9-alpine

WORKDIR /app

# Install required system packages
RUN apk add --no-cache gcc musl-dev linux-headers

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
