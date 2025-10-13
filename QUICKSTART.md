# Library gRPC Service - Complete Quickstart Guide

This guide will help you start the entire Library gRPC service from scratch, assuming you just came online.

## Prerequisites

Make sure you have the following installed:
- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 1.29 or higher)
- **grpcurl** (for testing) - Install: `brew install grpcurl` (Mac) or `go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest`

Verify installations:
```bash
docker --version
docker compose version
grpcurl --version
```

## Step 1: Clean Up (if needed)

If you have any existing containers or volumes from previous runs:

```bash
# Stop and remove all related containers
docker compose -f docker/docker-compose.yml down -v

# Or manually stop/remove old containers
docker stop mysql-container mongo-db library-grpc-server 2>/dev/null || true
docker rm mysql-container mongo-db library-grpc-server 2>/dev/null || true

# Remove old volumes (WARNING: This deletes all data)
docker volume rm mysql_data mongo_data 2>/dev/null || true
```

## Step 2: Start Everything

From the project root directory:

```bash
# Start all services (MySQL, MongoDB, gRPC server)
docker compose -f docker/docker-compose.yml up -d --build
```

This single command will:
1. Build the gRPC server Docker image
2. Start MySQL container
3. Start MongoDB container
4. Wait for databases to be healthy
5. Run database migrations automatically
6. Seed databases with sample data
7. Start the gRPC server

## Step 3: Verify Everything is Running

Check that all services are up:

```bash
docker compose -f docker/docker-compose.yml ps
```

You should see 3 services running:
- `mysql-container` (healthy)
- `mongo-db` (healthy)
- `library-grpc-server` (running)

View logs to confirm startup:

```bash
docker compose -f docker/docker-compose.yml logs -f grpc-server
```

## Step 4: Test the API

Now test each endpoint with grpcurl:

### 1. Get Inventory Summary
```bash
grpcurl -plaintext -d '{}' localhost:50051 Library/GetInventorySummary
```

Expected output: List of all books with ISBNs, titles, authors, and copies

### 2. Get Books for a Patron
```bash
# Patron ID 1 (John Doe)
grpcurl -plaintext -d '{"patron_id": 1}' localhost:50051 Library/GetBooks

# Patron ID 2 (Jane Doe)
grpcurl -plaintext -d '{"patron_id": 2}' localhost:50051 Library/GetBooks
```

### 3. Register a New Patron
```bash
grpcurl -plaintext -d '{"patron": "Alice"}' localhost:50051 Library/RegisterPatron
```

Expected: `{"message": "Successfully registered patron \"Alice\""}`

### 4. Get Book Count
```bash
grpcurl -plaintext -d '{"book": "1984"}' localhost:50051 Library/GetBookCount
```

Expected: `{"copies_remaining": 1}`

### 5. Checkout a Book
```bash
grpcurl -plaintext -d '{"patron": "Alice", "book": "The Great Gatsby"}' localhost:50051 Library/CheckoutBook
```

Expected: `{"message": "Successfully checked out \"The Great Gatsby\"", "copies_remaining": 2}`

### 6. Verify Checkout (Get Alice's Books)
First, we need Alice's ID. Register her if you haven't:
```bash
# Get patron ID (Alice should be ID 3)
grpcurl -plaintext -d '{"patron_id": 3}' localhost:50051 Library/GetBooks
```

Expected: `{"isbns": ["9780061122415"]}`

### 7. Return a Book
```bash
grpcurl -plaintext -d '{"patron": "Alice", "book": "The Great Gatsby"}' localhost:50051 Library/ReturnBook
```

Expected: `{"message": "Successfully returned \"The Great Gatsby\"", "copies_remaining": 3}`

## Database Access

### MySQL
```bash
# Connect to MySQL
docker exec -it mysql-container mysql -uroot -ppassword my_database

# View books
SELECT * FROM Books;

# Exit
exit
```

### MongoDB
```bash
# Connect to MongoDB
docker exec -it mongo-db mongosh library

# View patrons
db.patrons.find().pretty()

# Exit
exit
```

## Stopping the Services

```bash
# Stop all services (keeps data)
docker compose -f docker/docker-compose.yml stop

# Stop and remove containers (keeps volumes/data)
docker compose -f docker/docker-compose.yml down

# Stop and remove everything including data
docker compose -f docker/docker-compose.yml down -v
```

## Development Workflow

### Making code changes:

1. Edit your code
2. Rebuild and restart:
   ```bash
   docker compose -f docker/docker-compose.yml up -d --build grpc-server
   ```

3. View logs:
   ```bash
   docker compose -f docker/docker-compose.yml logs -f grpc-server
   ```

## Architecture Overview

```
┌──────────────────┐
│   grpcurl/Client │
└────────┬─────────┘
         │ gRPC (port 50051)
         ↓
┌──────────────────────┐
│  gRPC Server         │
│  (Python)            │
├──────────────────────┤
│  Handler Layer       │
│  Controller Layer    │
│  Repository Layer    │
└────┬────────────┬────┘
     │            │
     ↓            ↓
┌─────────┐  ┌─────────┐
│  MySQL  │  │ MongoDB │
│ (Books) │  │(Patrons)│
└─────────┘  └─────────┘
```
