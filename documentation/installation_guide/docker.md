
# 🚀 Docker Installation Guide

## 📌 Prerequisites
Ensure you have the following installed:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## 🛠 Install Docker
### **Linux (Ubuntu)**
```sh
sudo apt update && sudo apt install -y docker.io docker-compose
```

### **macOS (Homebrew)**
```sh
brew install --cask docker
brew install docker-compose
```

### **Windows**
Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop).

---

## 🏗️ Build and Run Containers
Navigate to the project directory and run:
```sh
docker-compose up -d --build
```

This will:
- Build and start all containers in **detached mode (`-d`)**.
- Automatically apply environment variables from `docker-compose.yml`.

---

## 📜 Useful Docker Commands
### View Running Containers
```sh
docker ps
```

### Check Logs for Web Service
```sh
docker logs web
```

### Restart Containers
```sh
docker-compose restart
```

### Stop and Remove Containers
```sh
docker-compose down -v
```

---

## ✅ Verifying Setup
### Check if ArangoDB is Running
```sh
curl http://localhost:8529
```
✅ If successful, you should see a JSON response from ArangoDB.

### Check if Django is Running
Visit:
```
http://localhost:8000
```
If you see the Django welcome page or your application UI, everything is working fine! 🎉

---

## 🔧 Troubleshooting
### **Container is not running?**
Run:
```sh
docker-compose ps
```
If any service is **stopped**, restart with:
```sh
docker-compose up -d
```

### **Check if ArangoDB is responding**
Inside the Django container, run:
```sh
docker exec -it web curl http://arangodb:8529
```
If the response is empty, ArangoDB might have failed to start.

### **Rebuild everything (Hard Reset)**
If containers are behaving unexpectedly:
```sh
docker-compose down -v
sudo docker system prune -a
sudo docker volume prune
sudo docker-compose up -d --build
```

---

🎯 **Now your Docker environment is set up and running!** 🚀

