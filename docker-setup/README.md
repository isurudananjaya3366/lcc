# LankaCommerce Cloud — Docker Setup Tool

A guided GUI tool for setting up the LankaCommerce Cloud development environment on Windows with Docker Desktop.

## Prerequisites

| Requirement            | Where to get it                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **Python 3.8+**        | [python.org/downloads](https://www.python.org/downloads/) — check **"Add Python to PATH"** |
| **Docker Desktop**     | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)      |
| **8 GB RAM** (minimum) | —                                                                                          |
| Internet connection    | For pulling Docker images                                                                  |

## How to Run

1. Make sure Docker Desktop is **open and running** (green whale icon in the system tray)
2. Double-click **`setup.vbs`** in this folder
3. The setup GUI will open automatically
4. Click **▶ Start Setup** and follow the on-screen progress

> The first run downloads ~2–3 GB of Docker images. It may take 10–20 minutes depending on your internet speed.

## What the Tool Does

| Step                | What happens                                                          |
| ------------------- | --------------------------------------------------------------------- |
| Prerequisites check | Verifies Python, Docker, Git, and required ports                      |
| Environment files   | Creates `.env.docker` and `docker-compose.override.yml` from examples |
| Docker images       | Pulls all service images from Docker Hub                              |
| Start services      | Starts all 8 services in background                                   |
| Health check        | Waits for every service to be ready (up to 5 min)                     |
| Verification        | Tests backend and frontend HTTP endpoints                             |

## Application URLs (after setup)

| App                  | URL                             |
| -------------------- | ------------------------------- |
| **Frontend (Login)** | http://localhost:3000/login     |
| **Dashboard**        | http://localhost:3000/dashboard |
| **Backend API**      | http://localhost:8001/api/v1/   |
| **Celery Monitor**   | http://localhost:5555/          |

## Default Credentials

```
Email:    admin@lcc.lk
Password: Admin1234x
```

## Troubleshooting

**"Python Not Found" error from setup.vbs**

- Install Python from python.org
- During installation, check **"Add Python to PATH"**
- Restart your computer and try again

**Docker Desktop not starting / setup fails at Step 4**

- Open Docker Desktop manually
- Wait for the whale icon in the system tray to stop animating
- Click Retry in the setup tool

**Port already in use (e.g. 5432)**

- Another app (like a local PostgreSQL) is using that port
- Stop the conflicting service or let the setup continue — Docker will warn but usually still works

**Services never become healthy**

- Run `docker compose logs backend` in a terminal inside the project folder
- The backend may have failed due to a missing environment variable

**To stop all services later**

Open a terminal in the project folder (e.g. `C:\git_repos\pos`) and run:

```bash
docker compose down
```

Or to stop and remove all data:

```bash
docker compose down -v
```
