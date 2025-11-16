#!/bin/bash

# AI Video Editor - Production Deployment Script for Ubuntu VPS
# This script automates the deployment process on an Ubuntu server

set -e  # Exit on error

echo "🚀 AI Video Editor - Production Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root or with sudo${NC}"
    exit 1
fi

# Step 1: Update system
echo -e "${BLUE}📦 Updating system packages...${NC}"
apt update && apt upgrade -y

# Step 2: Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker...${NC}"
    apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

# Step 3: Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo -e "${BLUE}🐳 Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

# Step 4: Create application directory
APP_DIR="/var/www/video-editor"
echo -e "${BLUE}📁 Setting up application directory...${NC}"

if [ ! -d "$APP_DIR" ]; then
    mkdir -p "$APP_DIR"
fi

# Step 5: Copy application files
echo -e "${BLUE}📋 Copying application files...${NC}"
cp -r ./* "$APP_DIR/"
cd "$APP_DIR"

# Step 6: Set up production environment
echo -e "${BLUE}⚙️  Setting up production environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.production .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your production settings${NC}"
fi

# Step 7: Create necessary directories
mkdir -p uploads outputs temp
chmod 755 uploads outputs temp

# Step 8: Build and start containers
echo -e "${BLUE}🏗️  Building and starting Docker containers...${NC}"
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# Step 9: Wait for services to be healthy
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check if containers are running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
else
    echo -e "${RED}❌ Deployment failed. Check logs with: docker-compose -f docker-compose.prod.yml logs${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}Service URLs:${NC}"
echo "  Backend: http://localhost:3000"
echo "  AI Processor: http://localhost:5000"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart: docker-compose -f docker-compose.prod.yml restart"
echo "  Stop: docker-compose -f docker-compose.prod.yml down"
echo "  Update: ./deploy.sh"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Configure Nginx reverse proxy (see nginx.conf.example)"
echo "  2. Set up SSL with Let's Encrypt"
echo "  3. Configure firewall rules"
echo ""
