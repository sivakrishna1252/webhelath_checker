# Server Checker

A comprehensive Django-based server monitoring system that monitors your servers every few minutes and sends email alerts when issues are detected.

## Features

- **Automated Monitoring**: Monitors servers every 5 minutes (configurable)
- **Email Alerts**: Sends email notifications when servers go down
- **Recovery Notifications**: Optional recovery emails when servers come back online
- **Multiple Website Support**: Monitor multiple websites with separate configurations
- **Internal App Monitoring**: Monitor internal applications (frontend, backend, APIs, etc.)
- **Status Dashboard**: Beautiful web interface showing real-time status
- **Admin Interface**: Full Django admin for managing configurations
- **API Endpoints**: REST API for status information
- **No Spam**: Smart alerting prevents duplicate notifications

## Quick Start

### 1. Installation

```bash
# Clone or download the project
cd server-checker

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env file with your configuration
```

### 2. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 3. Configure Email Settings

Edit your `.env` file with your email configuration:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@serverchecker.com
```

### 4. Start the Services

```bash
# Terminal 1: Start Django development server
python manage.py runserver

# Terminal 2: Start Redis (if not already running)
redis-server

# Terminal 3: Start Celery worker
celery -A server_checker worker --loglevel=info

# Terminal 4: Start Celery beat (scheduler)
celery -A server_checker beat --loglevel=info
```

### 5. Access the Application

- **Main Dashboard**: http://localhost:8000/
- **Admin Interface**: http://localhost:8000/admin/
- **API Status**: http://localhost:8000/api/status/

## Usage

### Adding Websites

1. Go to the main dashboard
2. Click "Add Website"
3. Fill in the website details:
   - **Name**: Display name for the website
   - **URL**: Full URL to monitor (e.g., https://example.com)
   - **Alert Email**: Email address for alerts
   - **Recovery Email**: Optional separate email for recovery notifications
   - **Check Interval**: How often to check (default: 5 minutes)
   - **Timeout**: Request timeout (default: 30 seconds)

### Adding Internal Applications

1. Go to a website's detail page
2. Click "Add Internal App"
3. Configure the internal application:
   - **Name**: Name of the internal app
   - **Type**: Frontend, Backend, API, etc.
   - **URL**: Full URL to monitor
   - **Expected Status Code**: Usually 200

### Monitoring Configuration

- **Check Interval**: How often to check each website (in seconds)
- **Timeout**: How long to wait for a response before timing out
- **Expected Status Code**: HTTP status code that indicates success
- **Alert Cooldown**: Prevents spam by limiting duplicate alerts

## API Endpoints

### GET /api/status/

Returns JSON with current monitoring status:

```json
{
  "global_stats": {
    "total_websites": 5,
    "online_websites": 4,
    "offline_websites": 1,
    "total_internal_apps": 12,
    "online_internal_apps": 11,
    "offline_internal_apps": 1,
    "overall_uptime": 95.5
  },
  "websites": [
    {
      "id": 1,
      "name": "Example Website",
      "url": "https://example.com",
      "status": "online",
      "uptime_percentage": 99.2,
      "last_check": "2024-01-15T10:30:00Z",
      "response_time": 0.245
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Management Commands

### Manual Monitoring Check

```bash
# Check all websites
python manage.py run_monitoring

# Check specific website
python manage.py run_monitoring --website-id 1

# Check specific internal app
python manage.py run_monitoring --internal-app-id 1

# Force run even if monitoring is disabled
python manage.py run_monitoring --force
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | True |
| `ALLOWED_HOSTS` | Allowed hosts | localhost,127.0.0.1 |
| `EMAIL_HOST` | SMTP host | smtp.gmail.com |
| `EMAIL_PORT` | SMTP port | 587 |
| `EMAIL_USE_TLS` | Use TLS | True |
| `EMAIL_HOST_USER` | SMTP username | Required |
| `EMAIL_HOST_PASSWORD` | SMTP password | Required |
| `CELERY_BROKER_URL` | Redis URL | redis://localhost:6379/0 |
| `MONITORING_INTERVAL` | Check interval in seconds | 300 |

### Monitoring Settings

Access the Django admin to configure:
- Global monitoring settings
- Individual website configurations
- Internal application settings
- Alert logs and history

## Production Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

CMD ["gunicorn", "server_checker.wsgi:application"]
```

### Using Systemd

Create service files for:
- Django application
- Celery worker
- Celery beat
- Redis

### Using Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - db
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
  
  worker:
    build: .
    command: celery -A server_checker worker --loglevel=info
    depends_on:
      - redis
      - db
  
  beat:
    build: .
    command: celery -A server_checker beat --loglevel=info
    depends_on:
      - redis
      - db
  
  redis:
    image: redis:alpine
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: serverchecker
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
```

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP configuration and credentials
2. **Monitoring not running**: Ensure Celery worker and beat are running
3. **Database errors**: Run migrations with `python manage.py migrate`
4. **Redis connection**: Ensure Redis is running and accessible

### Logs

Check logs for:
- Django: Application logs
- Celery worker: Task execution logs
- Celery beat: Scheduler logs
- Redis: Database logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.





