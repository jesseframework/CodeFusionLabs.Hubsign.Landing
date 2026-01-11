#!/bin/bash
set -e

echo "🐳 Building HubSign Docker Images..."

# Build the Docker image
docker build -t hubsign-landing:latest .

echo "✅ Docker image built successfully!"
echo ""
echo "📦 Image: hubsign-landing:latest"
echo ""
echo "To run the application:"
echo "  Development: docker-compose up"
echo "  Production:  docker-compose -f docker-compose.prod.yml up -d"
