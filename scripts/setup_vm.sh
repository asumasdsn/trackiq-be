#!/bin/bash
# ================================================
# GCP e2 VM Setup Script for TrackIQ Backend
# Run this ONCE after creating your VM
# ================================================
set -e

echo "🔧 Updating system packages..."
sudo apt-get update -y && sudo apt-get upgrade -y

echo "🐳 Installing Docker..."
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "👤 Adding current user to docker group..."
sudo usermod -aG docker $USER

echo "🔑 Creating .env file (edit this with your real secrets)..."
cat <<EOF > ~/.env
OPENAI_API_KEY=your-openai-key-here
DATABASE_URL=sqlite:////app/trackiq.db
REDIS_URL=redis://localhost:6379
PROJECT_NAME=TrackIQ Backend
EOF

echo ""
echo "✅ VM setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Edit ~/.env with your real API keys"
echo "  2. Add these secrets to your GitHub repository:"
echo "     - GCP_VM_IP      → Your VM's external IP"
echo "     - GCP_VM_USER    → Your VM username (e.g. ubuntu)"
echo "     - GCP_SSH_PRIVATE_KEY → Your SSH private key"
echo ""
echo "  3. Push to main/dev branch to trigger auto-deploy!"
