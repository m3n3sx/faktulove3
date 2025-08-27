# Gunicorn Configuration for FaktuLove

## Overview

This document describes the Gunicorn configuration for the FaktuLove Django application.

## Configuration Files

### 1. Gunicorn Configuration (`gunicorn.conf.py`)

The main Gunicorn configuration file contains:

- **Server socket**: Binds to `127.0.0.1:8000`
- **Worker processes**: Automatically calculated based on CPU cores (`cpu_count * 2 + 1`)
- **Worker class**: `sync` (synchronous workers)
- **Logging**: Access and error logs in `/home/admin/faktulove/logs/`
- **Process management**: PID file at `/home/admin/faktulove/gunicorn.pid`

### 2. Systemd Service (`/etc/systemd/system/faktulove.service`)

The systemd service configuration:

```ini
[Unit]
Description=FaktuLove Django Application
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=admin
Group=admin
WorkingDirectory=/home/admin/faktulove
Environment="PATH=/home/admin/faktulove/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=faktulove.settings"
Environment="PYTHONPATH=/home/admin/faktulove"
ExecStart=/home/admin/faktulove/venv/bin/gunicorn --config /home/admin/faktulove/gunicorn.conf.py faktulove.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## Management Scripts

### 1. Start Script (`start_gunicorn.sh`)

Starts Gunicorn with proper environment setup.

### 2. Stop Script (`stop_gunicorn.sh`)

Gracefully stops Gunicorn using PID file or process name.

### 3. Restart Script (`restart_gunicorn.sh`)

Stops and starts Gunicorn in sequence.

### 4. Management Script (`manage_faktulove.sh`)

Comprehensive management script with commands:

- `status` - Show system status
- `start` - Start all services
- `stop` - Stop all services
- `restart` - Restart all services
- `logs` - Show recent logs
- `update` - Update from Git and restart

## Usage

### Starting the Service

```bash
# Using systemd (recommended)
sudo systemctl start faktulove.service

# Using management script
./manage_faktulove.sh start

# Manual start
./start_gunicorn.sh
```

### Stopping the Service

```bash
# Using systemd
sudo systemctl stop faktulove.service

# Using management script
./manage_faktulove.sh stop

# Manual stop
./stop_gunicorn.sh
```

### Checking Status

```bash
# System status
./manage_faktulove.sh status

# Service status
sudo systemctl status faktulove.service

# Process check
ps aux | grep gunicorn
```

### Viewing Logs

```bash
# Recent logs
./manage_faktulove.sh logs

# Gunicorn error logs
tail -f logs/gunicorn_error.log

# Gunicorn access logs
tail -f logs/gunicorn_access.log

# Systemd logs
sudo journalctl -u faktulove.service -f
```

## Configuration Details

### Worker Configuration

- **Worker count**: `cpu_count * 2 + 1` (automatically calculated)
- **Worker class**: `sync` (synchronous workers)
- **Max requests**: 1000 per worker
- **Max requests jitter**: 50
- **Worker connections**: 1000

### Logging Configuration

- **Access log**: `/home/admin/faktulove/logs/gunicorn_access.log`
- **Error log**: `/home/admin/faktulove/logs/gunicorn_error.log`
- **Log level**: `info`
- **Access log format**: Extended format with response time

### Security Configuration

- **User**: `admin`
- **Group**: `admin`
- **Bind address**: `127.0.0.1:8000` (localhost only)
- **Private temp**: Enabled
- **Timeout**: 5 seconds for stop

## Integration with Nginx

Gunicorn is configured to work with Nginx as a reverse proxy:

- Gunicorn listens on `127.0.0.1:8000`
- Nginx proxies requests from port 80 to Gunicorn
- Static files are served directly by Nginx
- Media files are served directly by Nginx

## Troubleshooting

### Common Issues

1. **Port already in use**: Check if another Gunicorn process is running
2. **Permission denied**: Ensure proper file permissions
3. **Import errors**: Check virtual environment activation
4. **Database connection**: Verify PostgreSQL is running

### Debug Commands

```bash
# Check if port is in use
ss -tlnp | grep :8000

# Check service status
sudo systemctl status faktulove.service

# Check logs
sudo journalctl -u faktulove.service -n 50

# Test application
curl -I http://localhost:8000/
```

## Performance Tuning

### Worker Count

The worker count is automatically calculated as `cpu_count * 2 + 1`. For manual tuning:

- **CPU-bound applications**: `cpu_count + 1`
- **I/O-bound applications**: `cpu_count * 2 + 1`
- **Memory-constrained**: Reduce worker count

### Memory Usage

Monitor memory usage with:

```bash
ps aux | grep gunicorn
free -h
```

### Load Testing

Test performance with:

```bash
# Simple load test
ab -n 1000 -c 10 http://localhost:8000/

# More comprehensive test
wrk -t12 -c400 -d30s http://localhost:8000/
```

## Monitoring

### Health Checks

```bash
# Application health
curl -f http://localhost:8000/ || echo "Application down"

# Service health
systemctl is-active faktulove.service
```

### Metrics

Key metrics to monitor:

- Response time
- Error rate
- Memory usage
- CPU usage
- Worker count
- Request rate

## Backup and Recovery

### Configuration Backup

```bash
# Backup configuration files
cp gunicorn.conf.py gunicorn.conf.py.backup
sudo cp /etc/systemd/system/faktulove.service /etc/systemd/system/faktulove.service.backup
```

### Recovery

```bash
# Restore configuration
cp gunicorn.conf.py.backup gunicorn.conf.py
sudo cp /etc/systemd/system/faktulove.service.backup /etc/systemd/system/faktulove.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart faktulove.service
```
