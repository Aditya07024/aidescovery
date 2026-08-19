# Production Server Deployment Guide

Target OS: **Ubuntu Linux** (SSH Server)

## 1. Server Preparation

```bash
# Update Ubuntu packages
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
sudo apt install -y docker.io docker-compose-v2 git
sudo systemctl enable --now docker
```

## 2. Clone Repository & Setup Environment

```bash
git clone https://github.com/your-org/universal-ai-discovery.git
cd universal-ai-discovery

cp .env.example .env
nano .env  # Update production secrets and DATABASE_URL
```

## 3. Launch Docker Compose Production Services

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

## 4. Execute Database Migrations

```bash
docker exec -it uadp_api_prod alembic upgrade head
```

## 5. Verify Health Probes

```bash
curl http://localhost/api/v1/health
curl http://localhost/api/v1/ready
```

## 6. Setup SSL / HTTPS with Let's Encrypt (Optional)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d discovery.yourdomain.com
```

## 7. Logs & Maintenance

```bash
# View backend logs
docker compose -f docker-compose.prod.yml logs -f api

# Restart services
docker compose -f docker-compose.prod.yml restart
```
