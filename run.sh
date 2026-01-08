#!/bin/bash

# ==========================================
# CONFIGURATION
# ==========================================
IMAGE_NAME="pefindo-transformer"
CONTAINER_NAME="pefindo-transformer-service"
PORT=8001

# Resource Limit
CPU_LIMIT="4.0"
MEM_LIMIT="4g"

# Output Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==========================================
# 1. BUILD IMAGE
# ==========================================
echo -e "${YELLOW}[1/3] Building Docker Image from ./app ...${NC}"
docker build -t $IMAGE_NAME ./app
if [ $? -ne 0 ]; then
    echo -e "${RED}BUILD FAILED! Aborting.${NC}"
    exit 1
fi

# ==========================================
# 2. CLEANUP OLD CONTAINER
# ==========================================
echo -e "${YELLOW}[2/3] Cleaning up old container...${NC}"
docker rm -f $CONTAINER_NAME 2>/dev/null || true

# ==========================================
# 3. RUN CONTAINER
# ==========================================
echo -e "${YELLOW}[3/3] Starting Container on Port $PORT ...${NC}"

# Note: Tidak ada flag -v (volume) karena tidak pakai file eksternal
docker run -d --name $CONTAINER_NAME -p $PORT:$PORT -v /opt/Middleware/Pefindo/logs/:/app/logs:Z -v /opt/Middleware/Pefindo/refcode.json:/app/data/dynamic/refcode.json:Z $IMAGE_NAME

# ==========================================
# STATUS CHECK
# ==========================================
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESS!${NC}"
    echo "----------------------------------------"
    echo "Container ID : $(docker ps -f name=$CONTAINER_NAME -q)"
    echo "Status       : Running"
    echo "Port         : $PORT"
    echo "Mode         : API Only (No XSLT)"
    echo "----------------------------------------"
    echo "Logs: docker logs -f $CONTAINER_NAME"
else
    echo -e "${RED}❌ DEPLOYMENT FAILED!${NC}"
fi