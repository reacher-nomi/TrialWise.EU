# Deploy the Live environment on Azure (one VM + Docker Compose)

The simplest reliable setup for a student prototype. About 30–45 minutes the first time.

## 1. Get Azure student credit

Sign up for **Azure for Students** with your university email (no credit card needed when eligible). Check the remaining credit in the Azure portal.

## 2. Create the VM

Azure Portal → **Virtual machines → Create**:

| Setting | Value |
|---|---|
| Region | **Germany West Central** (Frankfurt) – EU data location |
| Image | Ubuntu Server 24.04 LTS |
| Size | B2s (2 vCPU, 4 GB RAM) is enough. B1s is too small for Docker builds |
| Authentication | SSH public key |
| Inbound ports | **SSH (22)** and **HTTP (80)** |

Tip: set **Auto-shutdown** (VM → Operations) to save credit. Stop the VM when you're not demoing.

## 3. Install Docker on the VM

```bash
ssh azureuser@<VM-PUBLIC-IP>

curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit   # log out and back in so the group change applies
```

## 4. Get the code and start it

```bash
ssh azureuser@<VM-PUBLIC-IP>
git clone https://github.com/<your-org>/trialwise.git
cd trialwise
cp .env.example .env
nano .env                       # set a STRONG DB_PASSWORD, APP_ENV=live
docker compose -f docker-compose.prod.yml up -d --build
```

Open `http://<VM-PUBLIC-IP>` in your browser. 🎉

## 5. Update after new commits

```bash
cd trialwise && git pull
docker compose -f docker-compose.prod.yml up -d --build
```

## Later (optional improvements)

- **HTTPS**: add a domain + Caddy or Certbot (needed before any real users).
- **Auto-deploy**: a GitHub Actions job that SSHes into the VM and runs the update commands on every merge to `main`.
- **Backups**: `docker compose exec db pg_dump -U app trialwise > backup.sql`.

## Troubleshooting

| Problem | Fix |
|---|---|
| Page doesn't load | Check port 80 is open in the VM's **Networking** settings |
| `permission denied` with docker | You didn't log out/in after `usermod` |
| Backend restarting | `docker compose -f docker-compose.prod.yml logs backend` |
| Build killed / very slow | VM too small. Resize to B2s |
