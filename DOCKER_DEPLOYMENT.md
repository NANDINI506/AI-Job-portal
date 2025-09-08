# 🐳 Docker Deployment Guide for Job Portal

This guide provides step-by-step instructions to containerize and deploy your AI-powered Job Portal using Docker.

## 📋 Prerequisites

Before starting, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (to clone the repository)

### Installing Docker

#### Windows:

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and restart your computer
3. Verify installation: `docker --version`

#### macOS:

1. Download Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. Install and restart your computer
3. Verify installation: `docker --version`

#### Linux (Ubuntu/Debian):

```bash
# Update package index
sudo apt-get update

# Install Docker
sudo apt-get install docker.io docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, then verify
docker --version
```

## 🚀 Quick Start (Development)

### Step 1: Clone and Setup

```bash
# Clone your repository
git clone <your-repository-url>
cd job-portal

# Copy environment file
cp env.example .env
```

### Step 2: Configure Environment

Edit the `.env` file with your actual values:

```bash
# Required: Email Configuration
EMAIL_SENDER=your-email@gmail.com
GMAIL_APP_PASSWORD=your-gmail-app-password

# Required: AI Configuration
GEMINI_API_KEY=your-gemini-api-key

# Optional: Database (default is fine for development)
DATABASE_URL=sqlite:///./jobs.db
```

### Step 3: Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f
```

### Step 4: Access the Application

- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Login**:
  - Username: `admin`
  - Password: `admin`

## 🏭 Production Deployment

### Step 1: Production Environment Setup

```bash
# Create production environment file
cp env.example .env.production

# Edit production settings
nano .env.production
```

Production `.env` configuration:

```env
# Email Configuration
EMAIL_SENDER=your-production-email@gmail.com
GMAIL_APP_PASSWORD=your-production-app-password

# AI Configuration
GEMINI_API_KEY=your-production-gemini-api-key

# Database Configuration
DATABASE_URL=sqlite:///./jobs.db

# Security
SECRET_KEY=your-very-secure-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=info
```

### Step 2: Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  job-portal:
    build: .
    container_name: job-portal-prod
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./jobs.db
      - STATIC_DIR=/app/app/static
      - RESUMES_DIR=/app/resumes
      - TEMPLATES_DIR=/app/app/templates
    env_file:
      - .env.production
    volumes:
      - ./resumes:/app/resumes
      - ./jobs.db:/app/jobs.db
      - ./app/static:/app/app/static
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    container_name: job-portal-nginx-prod
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - job-portal
    restart: unless-stopped
```

### Step 3: Deploy to Production

```bash
# Build production image
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🔧 Docker Commands Reference

### Basic Commands

```bash
# Build the image
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update and restart
docker-compose up -d --build
```

### Development Commands

```bash
# Run in development mode with live reload
docker-compose up

# Execute commands in running container
docker-compose exec job-portal bash

# View container logs
docker-compose logs job-portal

# Check container status
docker-compose ps
```

### Database Commands

```bash
# Access database (if using external DB)
docker-compose exec job-portal python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Backup database
docker cp job-portal:/app/jobs.db ./backup_jobs.db

# Restore database
docker cp ./backup_jobs.db job-portal:/app/jobs.db
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using port 8000
netstat -tulpn | grep :8000

# Kill the process or change port in docker-compose.yml
```

#### 2. Permission Issues

```bash
# Fix file permissions
sudo chown -R $USER:$USER ./resumes
sudo chown -R $USER:$USER ./app/static
```

#### 3. Environment Variables Not Loading

```bash
# Check if .env file exists and has correct format
cat .env

# Verify environment variables in container
docker-compose exec job-portal env
```

#### 4. Database Issues

```bash
# Recreate database
docker-compose down
rm jobs.db
docker-compose up -d
```

#### 5. Build Failures

```bash
# Clean build
docker-compose down
docker system prune -f
docker-compose build --no-cache
```

### Debugging Commands

```bash
# Check container health
docker-compose ps

# View detailed logs
docker-compose logs --tail=100 job-portal

# Access container shell
docker-compose exec job-portal bash

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -f
```

## 📊 Monitoring and Maintenance

### Health Checks

The application includes built-in health checks:

```bash
# Check application health
curl http://localhost:8000/

# Check container health
docker-compose ps
```

### Log Management

```bash
# View real-time logs
docker-compose logs -f job-portal

# Save logs to file
docker-compose logs job-portal > app.log

# Rotate logs (add to crontab)
0 0 * * * docker-compose logs --since=24h job-portal > /var/log/job-portal-$(date +\%Y\%m\%d).log
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh - Daily backup script

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/job-portal"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker cp job-portal:/app/jobs.db $BACKUP_DIR/jobs_$DATE.db

# Backup resumes
tar -czf $BACKUP_DIR/resumes_$DATE.tar.gz ./resumes/

# Clean old backups (keep 7 days)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## 🔒 Security Considerations

### Production Security

1. **Change Default Passwords**:

   - Update admin credentials
   - Use strong passwords

2. **Environment Variables**:

   - Never commit `.env` files
   - Use secure secret management

3. **Network Security**:

   - Use HTTPS in production
   - Configure firewall rules
   - Limit exposed ports

4. **Container Security**:
   - Keep base images updated
   - Run containers as non-root user
   - Use security scanning tools

### SSL/HTTPS Setup

```bash
# Generate SSL certificates (using Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates to ssl directory
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./ssl/
```

## 📈 Scaling and Performance

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: "3.8"

services:
  job-portal:
    build: .
    deploy:
      replicas: 3
    # ... other configuration
```

```bash
# Scale the application
docker-compose -f docker-compose.scale.yml up -d --scale job-portal=3
```

### Performance Optimization

1. **Resource Limits**:

```yaml
services:
  job-portal:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "1.0"
          memory: 1G
```

2. **Caching**:
   - Use Redis for session storage
   - Implement application-level caching
   - Use CDN for static assets

## 🚀 Deployment to Cloud Platforms

### AWS ECS

1. Push image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Set up auto-scaling

### Google Cloud Run

1. Build and push to Container Registry
2. Deploy to Cloud Run
3. Configure custom domain
4. Set up monitoring

### Azure Container Instances

1. Push to Azure Container Registry
2. Deploy to Container Instances
3. Configure networking
4. Set up monitoring

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables
3. Check Docker and Docker Compose versions
4. Review the troubleshooting section above

For additional help, create an issue in the repository or contact the development team.

---

**Happy Deploying! 🚀**
