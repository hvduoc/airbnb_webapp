# Production Deployment Commands (run trong Codespace)

# 1. Make deploy script executable
chmod +x deploy-production.sh

# 2. Copy script to VPS
scp deploy-production.sh root@YOUR_SERVER_IP:/tmp/

# 3. SSH vào VPS và chạy deployment
ssh root@YOUR_SERVER_IP

# 4. Trong VPS, run deployment script:
cd /tmp
chmod +x deploy-production.sh
./deploy-production.sh

# Script sẽ tự động:
# - Update system
# - Install nginx, python, node
# - Clone repo từ GitHub  
# - Setup systemd services
# - Configure nginx reverse proxy
# - Start all services

# 5. Check services status:
sudo systemctl status airbnb-api airbnb-webhook airbnb-brain nginx

# 6. Test local access:
curl http://localhost:8080/health
curl http://localhost:8000/
curl http://localhost:3000/