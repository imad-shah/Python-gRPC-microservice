# Docker Setup for Library gRPC Service

This document explains how to run the Library gRPC service using Docker Compose.

## Prerequisites

- Docker installed and running
- Docker Compose installed

## Services

The Docker Compose setup includes three services:

1. **MySQL** (mysql-container) - Port 3306
   - Database: `my_database`
   - Root password: `password`
   - Volume: `mysql_data`

2. **MongoDB** (mongo-db) - Port 27017
   - Database: `library`
   - Collection: `patrons`
   - Volume: `mongo_data`

3. **gRPC Server** (library-grpc-server) - Port 50051
   - Handles library management operations
   - Depends on MySQL and MongoDB being healthy

## Quick Start

### Start all services

```bash
docker-compose up -d
```

This will:
- Start MySQL and MongoDB containers
- Wait for databases to be healthy
- Build and start the gRPC server

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f grpc-server
docker-compose logs -f mysql
docker-compose logs -f mongodb
```

### Stop services

```bash
docker-compose down
```

### Stop and remove volumes (WARNING: This deletes all data)

```bash
docker-compose down -v
```

## Using Existing Containers

If you already have MySQL and MongoDB containers running (like `mysql-container` and `mongo-db`), you have two options:

### Option 1: Stop existing containers and use Docker Compose

```bash
# Stop existing containers
docker stop mysql-container mongo-db

# Start with Docker Compose
docker-compose up -d
```

### Option 2: Run only the gRPC server

If you want to keep your existing database containers:

```bash
# Build the gRPC server image
docker build -t library-grpc-server .

# Run the gRPC server (connecting to existing containers)
docker run -d \
  --name library-grpc-server \
  --network bridge \
  -p 50051:50051 \
  -e MYSQL_HOST=localhost \
  -e MYSQL_USER=root \
  -e MYSQL_PASSWORD=password \
  -e MYSQL_DATABASE=my_database \
  -e MONGO_URI=mongodb://localhost:27017/ \
  library-grpc-server
```

## Environment Variables

The gRPC server accepts these environment variables:

- `MYSQL_HOST` - MySQL hostname (default: localhost)
- `MYSQL_USER` - MySQL user (default: root)
- `MYSQL_PASSWORD` - MySQL password (default: password)
- `MYSQL_DATABASE` - MySQL database name (default: my_database)
- `MONGO_URI` - MongoDB connection URI (default: mongodb://localhost:27017/)

## Database Initialization

### MySQL Schema

Run your migrations to create the books table:

```bash
# Copy migration SQL to container
docker cp migrations/create_books_table.sql mysql-container:/tmp/

# Execute migration
docker exec -i mysql-container mysql -uroot -ppassword my_database < migrations/create_books_table.sql
```

### MongoDB Collections

MongoDB collections are created automatically when first accessed.

## Troubleshooting

### Check service health

```bash
docker-compose ps
```

### Check container logs

```bash
docker-compose logs grpc-server
```

### Connect to MySQL

```bash
docker exec -it mysql-container mysql -uroot -ppassword my_database
```

### Connect to MongoDB

```bash
docker exec -it mongo-db mongosh library
```

### Rebuild gRPC server

```bash
docker-compose up -d --build grpc-server
```

## Development

For local development without Docker:

1. Ensure MySQL and MongoDB are running locally or via Docker
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python main.py`

The application will connect to localhost databases by default.
