# Medianova Uptime Monitor

A simple uptime monitoring application that checks the availability of medianova.com every minute.

## Features

- Monitors medianova.com every 60 seconds
- Logs response times and status codes
- Runs with 2 replicas for high availability
- Uses Nginx as a load balancer

## Prerequisites

- Docker
- Docker Compose

## Running the Application

1. Clone the repository:
```bash
git clone <repository-url>
cd medianova-uptime-monitor
```

2. Start the application:
```bash
docker-compose up -d
```

3. View the logs:
```bash
docker-compose logs -f
```

## Architecture

The application consists of:
- 2 replicas of the monitoring application
- 1 Nginx load balancer
- A shared Docker network for communication

## Monitoring

The application logs:
- Site status (UP/DOWN)
- Response time
- HTTP status codes
- Any errors that occur during monitoring

## Stopping the Application

To stop the application:
```bash
docker-compose down
```

## Docker Setup Details

- **Python Version:** The application runs on Python 3.9 (as specified in the Dockerfile).
- **Dependencies:** All Python dependencies are listed in `requirements.txt` and installed in a virtual environment during the build process.
- **Services:**
  - `python-app`: The main monitoring application, built from the provided Dockerfile. Runs as a non-root user for security. Two replicas are deployed for high availability.
  - `python-nginx`: Nginx acts as a load balancer for the monitoring app. The configuration is provided via `nginx.conf`.
- **Networks:** Both services communicate over a custom Docker bridge network (`appnet`).
- **Ports:**
  - The Nginx service exposes port **80** on the host, forwarding traffic to the monitoring app replicas.
  - The monitoring app itself does not expose any ports directly; it is accessed via Nginx.
- **Environment Variables:** No required environment variables are specified by default. If you need to add any, you can use a `.env` file and uncomment the `env_file` line in `docker-compose.yml`.
- **Special Configuration:**
  - The Nginx configuration is mounted from `nginx.conf` in the project root. You can customize this file to adjust load balancing or proxy settings.
  - The application is designed to be run with at least two replicas for redundancy, as configured in the Compose file.

For any customizations, edit the `nginx.conf` or `docker-compose.yml` as needed.