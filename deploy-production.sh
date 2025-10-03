#!/bin/bash
# deploy-production.sh - Auto deployment script

echo "🚀 Deploying Airbnb WebApp to production..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies  
sudo apt install -y nginx python3 python3-pip python3-venv git nodejs npm

# Setup application
cd /opt
if [ ! -d "airbnb_webapp" ]; then
    git clone https://github.com/hvduoc/airbnb_webapp.git
fi

cd airbnb_webapp
git pull origin main

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Node.js dependencies
cd brain-ui
npm install
npm run build
cd ..

# Create systemd services
sudo tee /etc/systemd/system/airbnb-api.service > /dev/null <<EOF
[Unit]
Description=Airbnb API Service
After=network.target

[Service]
Type=simple  
User=root
WorkingDirectory=/opt/airbnb_webapp
Environment=PATH=/opt/airbnb_webapp/venv/bin
ExecStart=/opt/airbnb_webapp/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/airbnb-webhook.service > /dev/null <<EOF
[Unit]
Description=Airbnb Webhook Service
After=network.target

[Service]
Type=simple
User=root  
WorkingDirectory=/opt/airbnb_webapp
Environment=PATH=/opt/airbnb_webapp/venv/bin
ExecStart=/opt/airbnb_webapp/venv/bin/uvicorn webhook_listener:app --host 0.0.0.0 --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo tee /etc/systemd/system/airbnb-brain.service > /dev/null <<EOF
[Unit]
Description=Airbnb Brain UI Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/airbnb_webapp/brain-ui  
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 3000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Nginx configuration
sudo tee /etc/nginx/sites-available/xemgiadat > /dev/null <<EOF
server {
    listen 80;
    server_name brain.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    server_name webhook.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

server {
    listen 80;
    server_name api.xemgiadat.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable airbnb-api airbnb-webhook airbnb-brain nginx
sudo ln -sf /etc/nginx/sites-available/xemgiadat /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
sudo systemctl start airbnb-api airbnb-webhook airbnb-brain
sudo systemctl reload nginx

# Firewall setup
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

echo "✅ Deployment complete!"
echo "🌐 URLs:"
echo "   Brain UI: https://brain.xemgiadat.com"
echo "   API: https://api.xemgiadat.com"  
echo "   Webhook: https://webhook.xemgiadat.com/webhook/github"
echo ""
echo "📋 Next steps:"
echo "1. Update Cloudflare DNS với server IP"
echo "2. Configure GitHub webhook"
echo "3. Test the integration"