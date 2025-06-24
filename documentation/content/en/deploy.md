---
title: Deployment
date: 2025-05-20
author: nestessia
tags: [deployment, hosting, server]
format: markdown
template: en_page.html
language: en
---

# 🌐 Deployment

This section covers various ways to deploy a site created with StaticFlow.

## 🚀 Preparing for deployment

### 📦 Building the site

```bash
staticflow build
```

This will create static files in the `output/` directory.

### ✅ Checking the build

```bash
staticflow serve --build-dir output
```

## 🏠 Hosting options

### 🐙 GitHub Pages

1. Create a `username.github.io` repository
2. Configure GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install staticflow
          
      - name: Build site
        run: staticflow build
        
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./output
```

### ⚡ Netlify

1. Create `netlify.toml`:

```toml
[build]
  command = "staticflow build"
  publish = "output"

[build.environment]
  PYTHON_VERSION = "3.8"
```

2. Configure deployment:
   - Connect repository to Netlify
   - Specify build command: `staticflow build`
   - Specify publish directory: `output`

### 🚀 Vercel

1. Create `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "buildCommand": "staticflow build",
        "outputDirectory": "output"
      }
    }
  ]
}
```

2. Create `package.json`:

```json
{
  "name": "my-staticflow-site",
  "version": "1.0.0",
  "scripts": {
    "build": "staticflow build"
  }
}
```

### ☁️ Amazon S3

1. Install AWS CLI:

```bash
pip install awscli
```

2. Configure AWS:

```bash
aws configure
```

3. Create deployment script:

```bash
#!/bin/bash
staticflow build
aws s3 sync output/ s3://your-bucket-name/ --delete
```

### 🐧 Nginx

1. Install Nginx:

```bash
sudo apt-get install nginx
```

2. Configure virtual host:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/your/output;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

3. Copy files:

```bash
sudo cp -r output/* /var/www/html/
```

## 🌍 Domain configuration

### 📡 DNS settings

1. Add A record:
```
your-domain.com.  A  your-server-ip
```

2. Add CNAME record for www:
```
www.your-domain.com.  CNAME  your-domain.com.
```

### 🔒 SSL certificate

#### 🔐 Let's Encrypt

1. Install Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Get certificate:

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Monitoring

### Logs

1. Configure logging in Nginx:

```nginx
access_log /var/log/nginx/your-domain.access.log;
error_log /var/log/nginx/your-domain.error.log;
```

2. Configure log rotation:

```nginx
logrotate /etc/logrotate.d/nginx
```

### Metrics

1. Install Prometheus:

```bash
sudo apt-get install prometheus
```

2. Configure Node Exporter:

```bash
sudo apt-get install prometheus-node-exporter
```

3. Configure Grafana:

```bash
sudo apt-get install grafana
```

## Backup

### Automatic backup

1. Create script:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
SITE_DIR="/path/to/site"
DATE=$(date +%Y-%m-%d)

tar -czf "$BACKUP_DIR/site-$DATE.tar.gz" "$SITE_DIR"
```

2. Add to crontab:

```bash
0 0 * * * /path/to/backup.sh
```

### Restoration

```bash
tar -xzf site-2024-03-20.tar.gz -C /path/to/restore
```

## Optimization

### Compression

1. Enable gzip in Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### Caching

1. Configure caching in Nginx:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
}
```

### CDN

1. Configure Cloudflare:
   - Add your domain
   - Update DNS records
   - Enable SSL
   - Configure caching

## Security

### Security headers

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-XSS-Protection "1; mode=block";
add_header X-Content-Type-Options "nosniff";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### DDoS protection

1. Configure rate limiting:

```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;

location / {
    limit_req zone=one burst=5;
}
```

### SSL/TLS

1. Configure modern ciphers:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
```

## Automation

### CI/CD

1. Configure GitHub Actions:

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
          
      - name: Build
        run: staticflow build
        
      - name: Deploy
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /path/to/site
            git pull
            staticflow build
            sudo systemctl reload nginx
```

### Deployment monitoring

1. Configure notifications:
   - Email
   - Slack
   - Telegram
   - Discord

2. Add checks:
   - Tests
   - Linting
   - Security checks 