# ATS Hybrid Architecture Setup

This guide explains how to connect your GitHub Codespace environment to your Laptop's database using Tailscale.

## Step 1: Laptop Setup (The Server)
1. Ensure your Laptop is running the ATS Docker containers:
   `docker compose up -d`
2. Ensure Tailscale is installed and running on your Windows laptop.
3. Open a command prompt or PowerShell and run the Tailscale Serve command to securely expose the local database to your Tailscale network:
   `tailscale serve --tcp 5432 tcp://127.0.0.1:5432`
4. Note your Laptop's Tailscale IP (e.g., `100.x.y.z`).

## Step 2: Codespace Setup (The Editor)
1. Start the GitHub Codespace. The `.devcontainer` setup will automatically install Tailscale.
2. In the Codespace terminal, start the Tailscale daemon and log in:
   `sudo tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &`
   `sudo tailscale up`
3. Click the link provided in the terminal to authenticate your Codespace to your Tailscale network.

## Step 3: Connect to the Database
1. In your Codespace, open `backend/.env`.
2. Update the `DATABASE_URL` to point to your laptop using the `ats_dev` user you created:
   `DATABASE_URL=postgresql+psycopg://ats_dev:ats_dev_password@[YOUR_LAPTOP_TAILSCALE_IP]:5432/ats_development`
3. Start the backend:
   `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
