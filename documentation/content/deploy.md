---
title: Развертывание
date: 2024-03-20
author: nastya
tags: [deployment, hosting, server]
format: markdown
template: page.html
---

# Развертывание

В этом разделе мы рассмотрим различные способы развертывания сайта, созданного с помощью StaticFlow.

## Подготовка к развертыванию

### Сборка сайта

```bash
staticflow build
```

Это создаст статические файлы в директории `output/`.

### Проверка сборки

```bash
staticflow serve --build-dir output
```

## Варианты хостинга

### GitHub Pages

1. Создайте репозиторий `username.github.io`
2. Настройте GitHub Actions:

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

### Netlify

1. Создайте `netlify.toml`:

```toml
[build]
  command = "staticflow build"
  publish = "output"

[build.environment]
  PYTHON_VERSION = "3.8"
```

2. Настройте деплой:
   - Подключите репозиторий к Netlify
   - Укажите команду сборки: `staticflow build`
   - Укажите директорию публикации: `output`

### Vercel

1. Создайте `vercel.json`:

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

2. Создайте `package.json`:

```json
{
  "name": "my-staticflow-site",
  "version": "1.0.0",
  "scripts": {
    "build": "staticflow build"
  }
}
```

### Amazon S3

1. Установите AWS CLI:

```bash
pip install awscli
```

2. Настройте AWS:

```bash
aws configure
```

3. Создайте скрипт деплоя:

```bash
#!/bin/bash
staticflow build
aws s3 sync output/ s3://your-bucket-name/ --delete
```

### Nginx

1. Установите Nginx:

```bash
sudo apt-get install nginx
```

2. Настройте виртуальный хост:

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

3. Скопируйте файлы:

```bash
sudo cp -r output/* /var/www/html/
```

## Настройка домена

### DNS настройки

1. Добавьте A-запись:
```
your-domain.com.  A  your-server-ip
```

2. Добавьте CNAME-запись для www:
```
www.your-domain.com.  CNAME  your-domain.com.
```

### SSL сертификат

#### Let's Encrypt

1. Установите Certbot:

```bash
sudo apt-get install certbot python3-certbot-nginx
```

2. Получите сертификат:

```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Мониторинг

### Логи

1. Настройте логирование в Nginx:

```nginx
access_log /var/log/nginx/your-domain.access.log;
error_log /var/log/nginx/your-domain.error.log;
```

2. Настройте ротацию логов:

```nginx
logrotate /etc/logrotate.d/nginx
```

### Метрики

1. Установите Prometheus:

```bash
sudo apt-get install prometheus
```

2. Настройте Node Exporter:

```bash
sudo apt-get install prometheus-node-exporter
```

3. Настройте Grafana:

```bash
sudo apt-get install grafana
```

## Резервное копирование

### Автоматическое резервное копирование

1. Создайте скрипт:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
SITE_DIR="/path/to/site"
DATE=$(date +%Y-%m-%d)

tar -czf "$BACKUP_DIR/site-$DATE.tar.gz" "$SITE_DIR"
```

2. Добавьте в crontab:

```bash
0 0 * * * /path/to/backup.sh
```

### Восстановление

```bash
tar -xzf site-2024-03-20.tar.gz -C /path/to/restore
```

## Оптимизация

### Сжатие

1. Включите gzip в Nginx:

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### Кэширование

1. Настройте кэширование в Nginx:

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
}
```

### CDN

1. Настройте Cloudflare:
   - Добавьте ваш домен
   - Обновите DNS записи
   - Включите SSL
   - Настройте кэширование

## Безопасность

### Заголовки безопасности

```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-XSS-Protection "1; mode=block";
add_header X-Content-Type-Options "nosniff";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

### Защита от DDoS

1. Настройте rate limiting:

```nginx
limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;

location / {
    limit_req zone=one burst=5;
}
```

### SSL/TLS

1. Настройте современные шифры:

```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
```

## Автоматизация

### CI/CD

1. Настройте GitHub Actions:

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
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install staticflow
          
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

### Мониторинг деплоя

1. Настройте уведомления:
   - Email
   - Slack
   - Telegram
   - Discord

2. Добавьте проверки:
   - Тесты
   - Линтинг
   - Проверка безопасности