---
title: Шаблоны
date: 2024-03-20
author: nastya
tags: [templates, jinja2, html]
format: markdown
template: page.html
---

# Шаблоны

В этом разделе мы рассмотрим, как работать с шаблонами в StaticFlow.

## Движок шаблонов

StaticFlow использует Jinja2 как движок шаблонов. Jinja2 предоставляет мощный и гибкий способ создания HTML шаблонов.

## Структура шаблонов

### Базовый шаблон

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{{ page.title }} - {{ config.site_name }}{% endblock %}</title>
    <meta name="description" content="{{ page.description }}">
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

    {% block extra_body %}{% endblock %}
</body>
</html>
```

### Шаблон страницы

```html
{% extends "base.html" %}

{% block content %}
<article>
    <h1>{{ page.title }}</h1>
    
    {% if page.date %}
    <time datetime="{{ page.date.isoformat() }}">
        {{ page.date.strftime('%d.%m.%Y') }}
    </time>
    {% endif %}

    {{ page.content }}
</article>
{% endblock %}
```

## Наследование шаблонов

### Базовый шаблон

```html
<!-- base.html -->
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

### Наследование

```html
<!-- page.html -->
{% extends "base.html" %}

{% block head %}
<title>{{ page.title }}</title>
{% endblock %}

{% block body %}
<h1>{{ page.title }}</h1>
{{ page.content }}
{% endblock %}
```

## Включение частичных шаблонов

### Создание частичного шаблона

```html
<!-- partials/navigation.html -->
<nav>
    <ul>
        <li><a href="/">Главная</a></li>
        <li><a href="/blog">Блог</a></li>
        <li><a href="/about">О нас</a></li>
    </ul>
</nav>
```

### Использование

```html
{% include "partials/navigation.html" %}
```

## Макросы

### Определение макроса

```html
<!-- macros.html -->
{% macro render_post(post) %}
<article>
    <h2>{{ post.title }}</h2>
    <time>{{ post.date.strftime('%d.%m.%Y') }}</time>
    {{ post.content }}
</article>
{% endmacro %}
```

### Использование макроса

```html
{% from "macros.html" import render_post %}

{% for post in posts %}
    {{ render_post(post) }}
{% endfor %}
```

## Переменные и контекст

### Доступные переменные

- `page` - текущая страница
- `config` - конфигурация сайта
- `site` - все страницы сайта
- `categories` - категории
- `tags` - теги
- `authors` - авторы

### Пример использования

```html
<h1>{{ page.title }}</h1>
<p>Автор: {{ page.author }}</p>
<p>Дата: {{ page.date.strftime('%d.%m.%Y') }}</p>

{% if page.tags %}
<p>Теги: 
    {% for tag in page.tags %}
    <a href="/tags/{{ tag }}">{{ tag }}</a>
    {% endfor %}
</p>
{% endif %}
```

## Фильтры

### Встроенные фильтры

```html
{{ page.title|upper }}
{{ page.content|truncate(200) }}
{{ page.date|date('%d.%m.%Y') }}
```

### Пользовательские фильтры

```python
# plugins/custom_filters.py
def markdown_to_html(text):
    return markdown.markdown(text)

def register_filters(app):
    app.jinja_env.filters['markdown'] = markdown_to_html
```

## Условные операторы

```html
{% if page.draft %}
<div class="draft-notice">Черновик</div>
{% endif %}

{% if page.tags %}
<p>Теги: {{ page.tags|join(', ') }}</p>
{% else %}
<p>Нет тегов</p>
{% endif %}
```

## Циклы

```html
{% for post in site.posts %}
<article>
    <h2>{{ post.title }}</h2>
    {{ post.content|truncate(200) }}
    <a href="{{ post.url }}">Читать далее</a>
</article>
{% endfor %}
```

## Шаблоны для разных типов контента

### Шаблон поста

```html
{% extends "base.html" %}

{% block content %}
<article class="post">
    <header>
        <h1>{{ page.title }}</h1>
        <div class="meta">
            <time>{{ page.date.strftime('%d.%m.%Y') }}</time>
            {% if page.author %}
            <span class="author">{{ page.author }}</span>
            {% endif %}
        </div>
    </header>

    {{ page.content }}

    {% if page.tags %}
    <footer>
        <div class="tags">
            {% for tag in page.tags %}
            <a href="/tags/{{ tag }}" class="tag">{{ tag }}</a>
            {% endfor %}
        </div>
    </footer>
    {% endif %}
</article>
{% endblock %}
```

### Шаблон категории

```html
{% extends "base.html" %}

{% block content %}
<h1>{{ page.title }}</h1>

<div class="posts">
    {% for post in page.posts %}
    <article>
        <h2><a href="{{ post.url }}">{{ post.title }}</a></h2>
        <time>{{ post.date.strftime('%d.%m.%Y') }}</time>
        {{ post.content|truncate(200) }}
    </article>
    {% endfor %}
</div>
{% endblock %}
```

## Плагины для шаблонов

- `staticflow-sass` - поддержка SASS/SCSS
- `staticflow-webpack` - сборка JavaScript
- `staticflow-images` - оптимизация изображений
- `staticflow-seo` - SEO оптимизация 