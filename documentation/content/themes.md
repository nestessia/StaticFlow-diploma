---
title: Темы
date: 2024-03-20
author: nastya
tags: [themes, templates, styling]
format: markdown
template: page.html
---

# Темы

В этом разделе мы рассмотрим, как работать с темами в StaticFlow.

## Что такое тема?

Тема в StaticFlow - это набор файлов, которые определяют внешний вид и функциональность сайта:

- HTML шаблоны
- CSS стили
- JavaScript файлы
- Изображения и другие медиафайлы
- Конфигурационные файлы

## Структура темы

```
theme/
├── templates/          # HTML шаблоны
│   ├── base.html      # Базовый шаблон
│   ├── page.html      # Шаблон страницы
│   ├── post.html      # Шаблон поста
│   └── partials/      # Частичные шаблоны
├── static/            # Статические файлы
│   ├── css/          # Стили
│   ├── js/           # Скрипты
│   └── images/       # Изображения
├── media/            # Медиафайлы
└── theme.toml        # Конфигурация темы
```

## Установка темы

### Через pip

```bash
pip install staticflow-theme-default
```

### Из репозитория

```bash
git clone https://github.com/staticflow/themes/default.git themes/default
```

## Использование темы

### В конфигурации

```toml
# config.toml
theme = "default"
```

### В шаблонах

```html
{% extends "theme/default/templates/base.html" %}
```

## Создание своей темы

### 1. Создание структуры

```bash
mkdir -p my-theme/{templates,static/{css,js,images},media}
touch my-theme/theme.toml
```

### 2. Конфигурация темы

```toml
# theme.toml
name = "My Theme"
version = "1.0.0"
author = "Your Name"
description = "A custom theme for StaticFlow"
license = "MIT"

[theme]
default_template = "base.html"
```

### 3. Базовый шаблон

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{{ page.title }}{% endblock %}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {% block extra_head %}{% endblock %}
</head>
<body>
    <header>
        {% include "partials/navigation.html" %}
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        {% include "partials/footer.html" %}
    </footer>

    <script src="/static/js/main.js"></script>
    {% block extra_body %}{% endblock %}
</body>
</html>
```

### 4. Стили

```css
/* static/css/style.css */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --background-color: #ffffff;
    --text-color: #212529;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background-color: var(--background-color);
}

/* ... другие стили ... */
```

### 5. JavaScript

```javascript
// static/js/main.js
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация темы
    initTheme();
});

function initTheme() {
    // Код инициализации
}
```

## Наследование тем

### Базовая тема

```html
<!-- base-theme/templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    {% block head %}{% endblock %}
</head>
<body>
    {% block body %}{% endblock %}
</body>
</html>
```

### Расширение темы

```html
<!-- my-theme/templates/base.html -->
{% extends "base-theme/templates/base.html" %}

{% block head %}
<title>{% block title %}{{ page.title }}{% endblock %}</title>
<link rel="stylesheet" href="/static/css/custom.css">
{% endblock %}

{% block body %}
<header class="custom-header">
    {% block header %}{% endblock %}
</header>

<main class="custom-main">
    {% block content %}{% endblock %}
</main>

<footer class="custom-footer">
    {% block footer %}{% endblock %}
</footer>
{% endblock %}
```

## Переопределение компонентов

### Переопределение стилей

```css
/* my-theme/static/css/custom.css */
:root {
    --primary-color: #ff0000;  /* Переопределение цвета */
}

.custom-header {
    /* Стили для кастомного хедера */
}
```

### Переопределение шаблонов

```html
<!-- my-theme/templates/partials/navigation.html -->
<nav class="custom-nav">
    <!-- Кастомная навигация -->
</nav>
```

## Плагины для тем

- `staticflow-theme-assets` - управление ресурсами темы
- `staticflow-theme-builder` - инструменты для создания тем
- `staticflow-theme-preview` - предпросмотр тем
- `staticflow-theme-export` - экспорт тем

## Лучшие практики

### Организация

1. Используйте модульную структуру
2. Разделяйте стили по компонентам
3. Минимизируйте зависимости
4. Документируйте компоненты

### Производительность

1. Оптимизируйте изображения
2. Минифицируйте CSS и JavaScript
3. Используйте кэширование
4. Следите за размером бандла

### Доступность

1. Используйте семантическую разметку
2. Обеспечьте поддержку клавиатурной навигации
3. Добавьте ARIA-атрибуты
4. Проверяйте контрастность

### Адаптивность

1. Используйте медиа-запросы
2. Тестируйте на разных устройствах
3. Применяйте mobile-first подход
4. Оптимизируйте изображения

## Публикация темы

### Подготовка

1. Создайте README.md
2. Добавьте лицензию
3. Напишите документацию
4. Создайте примеры

### Публикация

1. Создайте репозиторий
2. Настройте CI/CD
3. Опубликуйте в PyPI
4. Добавьте в каталог тем

## Обновление темы

### Версионирование

```toml
# theme.toml
version = "1.0.0"
```

### Миграции

1. Создайте миграционные скрипты
2. Документируйте изменения
3. Поддерживайте обратную совместимость
4. Тестируйте обновления
