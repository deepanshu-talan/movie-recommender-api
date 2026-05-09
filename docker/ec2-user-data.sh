#!/bin/bash
set -euo pipefail

# Log everything
exec > /var/log/user-data.log 2>&1
echo "=== MovieRecommender Setup Started: $(date) ==="

# 1. System updates
yum update -y

# 2. Install Docker
amazon-linux-extras install docker -y
systemctl start docker
systemctl enable docker
usermod -aG docker ec2-user

# 3. Install Docker Compose
COMPOSE_VERSION="2.24.6"
curl -SL "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-x86_64" \
  -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# 4. Install Git
yum install -y git

# 5. Clone the repository
cd /home/ec2-user
git clone https://github.com/deepanshu-talan/scalable-movie-recommendation-system.git app
cd app

# 6. Create .env file (REPLACE THE PLACEHOLDER WITH YOUR ACTUAL KEY)
cat > .env << 'ENVFILE'
TMDB_API_KEY=6892cfa019aa8128140103ad1628e357
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=$(openssl rand -hex 32)
REDIS_URL=redis://redis:6379/0
CACHE_ENABLED=1
SCHEDULER_ENABLED=1
API_VERSION=v1
LOG_LEVEL=INFO
ENVFILE

# Fix the SECRET_KEY (shell variable wasn't expanded inside heredoc)
SECRET=$(openssl rand -hex 32)
sed -i "s|SECRET_KEY=.*|SECRET_KEY=${SECRET}|" .env

# 7. Build and start with Docker Compose
cd docker
docker-compose up -d --build

# 8. Set permissions
chown -R ec2-user:ec2-user /home/ec2-user/app

echo "=== MovieRecommender Setup Completed: $(date) ==="
echo "App should be available on port 80"
