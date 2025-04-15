#!/bin/bash

# Build the project
echo "Building the project..."
npm run build

# Create a production-ready directory
echo "Creating production directory..."
mkdir -p production
cp -r dist/* production/

# Create a basic nginx configuration
echo "Creating nginx configuration..."
cat > production/nginx.conf <<EOL
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    root /var/www/html;
    index index.html;

    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # Enable gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
EOL

echo "Deployment files prepared in 'production' directory" 