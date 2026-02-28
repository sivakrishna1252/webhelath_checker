# Server Health Checker System

A comprehensive Django-based server monitoring system that actively monitors your websites and internal applications, tracks their uptime, measures response times, and sends customized email alerts when issues are detected.

---

## 🔍 How we identify if a Server is "UP" or "DOWN"

The core logic of this system relies on a reliable continuous background worker (`background_monitor.py`) that checks your configured servers and applications against an ongoing schedule (usually every 60 seconds).

### The server is considered **UP (Online)** when:
1. A secure networking connection to the server is successfully established.
2. The server responds fully within your configured **timeout duration**.
3. The HTTP Status Code returned by the server **matches** the "Expected Status Code" configured for that specific website (e.g., `200 OK`).

### The server is considered **DOWN (Offline)** when:
1. **Timeout error**: The server fails to respond within the configured timeout threshold.
2. **Invalid Status Code**: The server returns an unexpected status code (e.g., `500 Internal Server Error`, `502 Bad Gateway`, `401 Unauthorized` or `404 Not Found`).
3. **Connection error**: The server actively refuses the connection, drops packets, or a DNS resolution fails entirely.

When a server transitions to **DOWN**, the system captures the exact raw response code, logs the timeout instance, and immediately dispatches an email alert to the platform's administrator ensuring visibility of the breakdown.

---

## ⚡ Architecture & Workflow

1. **Dashboard Frontend (Django)**: 
   - A beautiful frontend UI structure mapping your URLs, configuring email thresholds, determining check intervals, and visualizing real-time analytical uptime & metrics.
2. **Background Monitor Worker (`background_monitor.py`)**: 
   - A standalone Python thread worker utilizing `ThreadPoolExecutor`. It actively polls the database for all active online URLs, runs rapid parallel HTTP probes reliably without slowing the Django main thread, evaluates the endpoints against safety checks, and stores the response results down into our SQL storage safely.
3. **Alerting System (`services.py`)**:
   - Actively checks the background health stats compared to previous historic loops. It uses Django's `send_mail` SMTP backbone to send **Downtime Alerts** instantly and **Recovery Alerts** the moment stability is repaired.

---

## 🚀 Total Project Setup Guide

Follow these sequential steps to rapidly deploy and connect the overall architecture locally on Windows.

### 1. Prerequisites
- Python 3.8+
- Git (Optional)

### 2. Code Installation
Open your Command Prompt or PowerShell:

```bash
# Navigate to the workspace project directory
cd "C:\Users\VivekNookala\Desktop\server cheker"

# Create an isolated python virtual environment (Best Practice)
python -m venv venv
venv\Scripts\activate

# Install all mandatory library dependencies
pip install -r requirements.txt
```

### 3. Environment & Dynamic Configuration
```bash
# Replicate the structure of the environmental secrets file
copy .env.example .env
```
Open the newly created `.env` file using a text editor (like VSCode or Notepad) and paste in your correct live variables (crucially, the `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` settings required to trigger the emailing capability effectively).

### 4. Initializing the Database
The default database relies on SQLite. To generate tables, users data, and metric repositories, process the migrations:
```bash
python manage.py makemigrations
python manage.py migrate

# Register the administrative profile to access configurations
python manage.py createsuperuser
```

### 5. Launch the Whole Application Ecosystem
We have included a startup batch file to ease testing and development workflows. It bridges the Django environment alongside the background monitoring threads simultaneously.

Simply click the file within your explorer:
`start_all.bat`

Or run via Terminal:
```bash
.\start_all.bat
```

This instantiates two core parallel channels:
1. **Dashboard Interface**: `http://127.0.0.1:8000/` (Visualize your stats, setup configs)
2. **Background Monitor Tracker**: The silent background loop handling the HTTP checks continuously inside terminal logging!

---

## ⚙️ How to Monitor & Use

1. Launch your favorite browser to `http://127.0.0.1:8000/` and access the user dashboard.
2. Locate the **Add Website** action.
3. Provide the endpoints details securely:
   - **Name**: e.g. "Main Ecommerce Server"
   - **URL**: e.g. `https://mysite.com/heartbeat`
   - **Alert Email** & **Recovery Email**: To specific developers needing alerts.
   - **Expected Status Code**: Mostly checking for `200`.
4. As soon as you validate the setup, the background worker will integrate the endpoint on its proceeding cycle and visually push metrics up into your application dynamically!

You may also bind individual **Internal Apps** (Frontend UI routers, API clusters, Redis nodes) directly below their main Website namespace for deep hierarchy control.
