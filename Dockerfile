FROM python:3.11-slim


#docker setup
#docker build -t server-checker .
#docker run -d -p 8000:8000 --name server-checker server-checker

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Expose standard port
EXPOSE 8000

# Default command (can be overridden by docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]



#docker setup
#docker build -t server-checker .
#docker run -d -p 8000:8000 --name server-checker server-checker

