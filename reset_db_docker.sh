#!/bin/bash
# Database reset script for Docker environment
# Usage: ./reset_db_docker.sh

echo "🗑️  Resetting Docker database..."

# Stop containers
echo "Stopping containers..."
docker-compose down

# Remove PostgreSQL volume (this wipes all data)
echo "Removing PostgreSQL data volume..."
docker volume rm practice3_postgres-data 2>/dev/null || echo "Volume already removed or doesn't exist"

# Start containers again (will create fresh database)
echo "Starting containers with fresh database..."
docker-compose up --build -d

echo "✅ Docker database reset complete!"
echo "📊 Fresh PostgreSQL database created"
echo "🌐 Access your app at http://localhost:3000"