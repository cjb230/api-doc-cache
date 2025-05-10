# Use a lightweight Python 3.13 base image
FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system -r requirements.txt

# Copy code
COPY app/ ./app/

# this line for local dev; override with real vars in prod
COPY .env .  

CMD ["python", "app/main.py"]
