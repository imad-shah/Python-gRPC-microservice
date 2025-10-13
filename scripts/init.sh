#!/bin/bash
set -e

echo "Waiting for MySQL to be ready..."
until mysql --skip-ssl -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" -e "SELECT 1" &> /dev/null
do
    echo "MySQL is unavailable - sleeping"
    sleep 2
done

echo "MySQL is up - running migrations..."
mysql --skip-ssl -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" < /app/migrations/create_table.sql
echo "MySQL table created"

echo "Seeding MySQL with sample data..."
mysql --skip-ssl -h "${MYSQL_HOST}" -u "${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "${MYSQL_DATABASE}" < /app/migrations/seed_data.sql
echo "MySQL seed data inserted"

echo "Waiting for MongoDB to be ready..."
until python3 -c "from pymongo import MongoClient; MongoClient('${MONGO_URI}', serverSelectionTimeoutMS=2000).admin.command('ping')" &> /dev/null
do
    echo "MongoDB is unavailable - sleeping"
    sleep 2
done

echo "MongoDB is up - running migrations..."
python3 /app/migrations/create_mongo_table.py
echo "MongoDB migrations complete"

echo "Starting gRPC server..."
exec python3 main.py
