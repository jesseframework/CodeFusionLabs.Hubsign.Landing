#!/bin/bash
set -e

# SSL Setup Script for HubSign Landing
# Usage: ./setup-ssl.sh your-domain.com your-email@domain.com

DOMAIN=${1:-hubsign.io}
EMAIL=${2:-admin@hubsign.io}

echo "🔒 Setting up SSL for $DOMAIN"
echo "📧 Using email: $EMAIL"
echo ""

# Create directories
mkdir -p certbot/conf
mkdir -p certbot/www

# Request certificate
echo "📜 Requesting SSL certificate from Let's Encrypt..."
docker-compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  -d $DOMAIN \
  -d www.$DOMAIN \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  --force-renewal

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSL certificate obtained successfully!"
    echo ""
    echo "📝 Next steps:"
    echo "1. Update nginx/nginx.conf with your domain name"
    echo "2. Restart nginx: docker-compose -f docker-compose.prod.yml restart nginx"
    echo "3. Test your site: https://$DOMAIN"
    echo ""
    echo "Certificate will auto-renew every 12 hours via certbot service"
else
    echo ""
    echo "❌ SSL certificate request failed!"
    echo ""
    echo "Common issues:"
    echo "- Domain DNS not pointing to this server"
    echo "- Port 80 not accessible"
    echo "- Domain verification failed"
    echo ""
    echo "Check logs: docker-compose -f docker-compose.prod.yml logs certbot"
fi
