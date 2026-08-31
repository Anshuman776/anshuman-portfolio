# Production Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying Anshuman Maurya's portfolio to production using Docker, Docker Compose, and Nginx.

## Prerequisites
- Docker & Docker Compose installed
- SSL certificates (self-signed or from Let's Encrypt)
- Domain name(s) pointing to your server
- Server with at least 1GB RAM and 10GB disk space

## File Structure
```
.
├── main.py                    # FastAPI application
├── data.py                    # Portfolio content
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container image definition
├── docker-compose.yml         # Multi-container orchestration
├── nginx.conf                 # Nginx reverse proxy config
├── .env                       # Environment variables (create from .env.example)
├── .env.example               # Example environment configuration
├── templates/                 # HTML templates
└── static/                    # CSS, JS, images
```

## Deployment Steps

### 1. Prepare Environment Variables
```bash
cp .env.example .env
# Edit .env with your actual values
nano .env
```

### 2. SSL Certificates Setup

#### Option A: Self-Signed Certificate (Testing)
```bash
mkdir -p certs
openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365
```

#### Option B: Let's Encrypt (Recommended for Production)
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d anshumanmaurya.in -d vstra.anshumanmaurya.in

# Copy certificates to your certs directory
sudo cp /etc/letsencrypt/live/anshumanmaurya.in/fullchain.pem certs/cert.pem
sudo cp /etc/letsencrypt/live/anshumanmaurya.in/privkey.pem certs/key.pem
sudo chmod 644 certs/cert.pem certs/key.pem
```

### 3. Build and Start Containers
```bash
# Build the Docker image
docker-compose build

# Start services in detached mode
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f portfolio-app
```

### 4. Verify Deployment
```bash
# Health check
curl http://localhost:8000/health

# Check portfolio endpoint
curl http://localhost:8000/

# View container logs
docker-compose logs
```

### 5. Configure Nginx Reverse Proxy

Update `nginx.conf` with your domain names and certificate paths, then restart Nginx:
```bash
docker-compose restart nginx
```

### 6. Set Up Auto-Renewal (Let's Encrypt)
```bash
# Create renewal script
sudo nano /usr/local/bin/renew-certs.sh

#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/anshumanmaurya.in/fullchain.pem /path/to/certs/cert.pem
cp /etc/letsencrypt/live/anshumanmaurya.in/privkey.pem /path/to/certs/key.pem
docker-compose -f /path/to/docker-compose.yml restart nginx

# Make executable
sudo chmod +x /usr/local/bin/renew-certs.sh

# Add to crontab for monthly renewal
sudo crontab -e
# Add: 0 0 1 * * /usr/local/bin/renew-certs.sh
```

## Production Checklist

- [ ] Environment variables configured in .env
- [ ] SSL certificates installed and paths updated in nginx.conf
- [ ] Docker and Docker Compose installed
- [ ] Ports 80 and 443 are accessible from the internet
- [ ] Domain names point to your server IP
- [ ] Health checks passing (`curl http://localhost:8000/health`)
- [ ] Logs are being captured and rotated
- [ ] Backup strategy for static files and templates
- [ ] Monitoring setup (optional: Prometheus, Grafana)
- [ ] Log aggregation configured (optional: ELK stack)

## Monitoring & Logs

### View Real-time Logs
```bash
docker-compose logs -f portfolio-app
docker-compose logs -f nginx
```

### Health Check
```bash
curl -s http://localhost:8000/health | jq .
```

### Performance Metrics
```bash
docker stats anshuman-portfolio anshuman-nginx
```

## Scaling & Performance

### Increase Worker Processes
Edit Dockerfile CMD:
```dockerfile
CMD ["gunicorn", "main:app", "--workers", "8", ...]
```

### Configure Load Balancing
Multiple instances behind Nginx:
```nginx
upstream portfolio {
    least_conn;
    server portfolio-app-1:8000;
    server portfolio-app-2:8000;
    server portfolio-app-3:8000;
}
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Container Fails to Start
```bash
# Check logs
docker-compose logs portfolio-app

# Rebuild image
docker-compose build --no-cache

# Try again
docker-compose up -d
```

### Certificate Issues
```bash
# Verify certificate validity
openssl x509 -in certs/cert.pem -text -noout

# Update certificate paths in nginx.conf
nano nginx.conf
docker-compose restart nginx
```

## Security Best Practices

1. **Keep Secrets Secure**
   - Never commit `.env` to version control
   - Use `.gitignore` to exclude sensitive files

2. **Regular Updates**
   ```bash
   docker-compose pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Backups**
   ```bash
   # Backup static files
   tar -czf backup-$(date +%Y%m%d).tar.gz static/ templates/
   ```

4. **Firewall Rules**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

## Rollback Procedure

```bash
# Stop current deployment
docker-compose down

# Restore from backup
tar -xzf backup-YYYYMMDD.tar.gz

# Restart services
docker-compose up -d
```

## Additional Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Docker Documentation: https://docs.docker.com/
- Nginx Documentation: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/
- Gunicorn Documentation: https://gunicorn.org/

## Support & Contact

For issues or questions, contact: anshumanmaurya776@gmail.com
