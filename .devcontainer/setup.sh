#!/bin/bash
set -e

echo "Setting up ATS Codespace environment..."

# 1. Install Tailscale
echo "Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# 2. Setup Python environment
echo "Setting up Python dependencies..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Setup Node environment
echo "Setting up Node dependencies..."
cd ../frontend
npm install

echo "========================================================"
echo "Setup Complete!"
echo ""
echo "To connect to your Laptop database, run:"
echo "sudo tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &"
echo "sudo tailscale up"
echo ""
echo "Then update your backend/.env with your Laptop's Tailscale IP."
echo "========================================================"
