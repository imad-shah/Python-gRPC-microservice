# 📚 Library gRPC Microservice

A Python-based **gRPC microservice** for managing a digital library system using a **hybrid database architecture (MySQL + MongoDB)**.  
Built with clean architecture principles, full Docker support, and automated database migrations.

---

## 🚀 Overview

The service provides gRPC endpoints for:
- 📘 **Book Management** – Track books, authors, ISBNs, and inventory  
- 🙋 **Patron Management** – Register patrons and view borrowed books  
- 🔁 **Checkout & Return** – Borrow or return books with automatic validation  
- 📊 **Inventory Summary** – View total titles, available copies, and checked-out counts  

Databases:
- **MySQL** → Relational data (Books)  
- **MongoDB** → Document data (Patrons)

---

## 🏗️ Tech Stack

- **Language:** Python 3.11  
- **API:** gRPC + Protocol Buffers  
- **Databases:** MySQL 8.0 & MongoDB 6  
- **Containerization:** Docker + Docker Compose  
- **Migrations:** Auto-run on startup  

---

## ⚡ Quick Start

> 📘 **For detailed step-by-step instructions and examples, see [QUICKSTART.md](QUICKSTART.md)**

```bash
# Clone and start containers
git clone <repo-url>
cd library_gRPC_py
docker compose -f docker/docker-compose.yml up -d --build

# Verify
grpcurl -plaintext -d '{}' localhost:50051 Library/GetInventorySummary
