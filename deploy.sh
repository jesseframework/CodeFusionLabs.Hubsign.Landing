#!/bin/bash
set -e

echo "🚀 Deploying HubSign to Production..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure it."
    exit 1
fi

# Build images
echo "📦 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Start new containers
echo "🚀 Starting new containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Run migrations
echo "🔄 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Check health
echo "🏥 Checking application health..."
sleep 5
curl -f http://localhost:8000/api/v1/health/ || echo "⚠️  Health check failed - check logs"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 View logs:    docker-compose -f docker-compose.prod.yml logs -f"
echo "🔍 View status:  docker-compose -f docker-compose.prod.yml ps"
echo "🛑 Stop:         docker-compose -f docker-compose.prod.yml down"
