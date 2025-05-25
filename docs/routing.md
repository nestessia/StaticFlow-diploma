# Маршрутизация в StaticFlow

## Обзор

StaticFlow использует гибкую систему маршрутизации, которая позволяет генерировать URL и пути файлов на основе метаданных контента. Система поддерживает различные типы контента и позволяет настраивать структуру URL.

## Типы контента

StaticFlow поддерживает следующие типы контента:

1. **page** - обычные страницы
2. **post** - посты блога
3. **tag** - страницы тегов
4. **category** - страницы категорий
5. **author** - страницы авторов
6. **index** - главная страница
7. **archive** - архивная страница

## URL паттерны

Каждый тип контента имеет свой паттерн URL:

```python
DEFAULT_URL_PATTERNS = {
    "page": "{category}/{slug}",                           
    "post": "{category_path}/{slug}",
    "tag": "{name}",
    "category": "{category_path}",
    "author": "{name}",
    "index": "",
    "archive": "archives"
}
```

## Паттерны сохранения файлов

Для каждого типа контента также определен паттерн сохранения файлов:

```python
DEFAULT_SAVE_AS_PATTERNS = {
    "page": "{category}/{slug}/index.html",  
    "post": "{category_path}/{slug}/index.html",
    "tag": "{name}/index.html",
    "category": "{category_path}/index.html",
    "author": "{name}/index.html",
    "index": "index.html",
    "archive": "archives/index.html"
}
```

## Метаданные

Для правильной генерации URL необходимо указать соответствующие метаданные в файлах контента:

### Страницы (page)
```yaml
---
title: "Заголовок страницы"
type: "page"
category: "about"  # Категория страницы
---
```

### Посты (post)
```yaml
---
title: "Заголовок поста"
type: "post"
category: "programming/python"  # Путь категории
date: 2024-05-25
author: "John Doe"
tags: ["python", "tutorial"]
---
```

### Теги (tag)
```yaml
---
title: "Python Posts"
type: "tag"
name: "python"  # Имя тега
---
```

### Категории (category)
```yaml
---
title: "Python Programming"
type: "category"
category_path: "programming/python"  # Путь категории
---
```

### Авторы (author)
```yaml
---
title: "John Doe's Posts"
type: "author"
name: "john-doe"  # Имя автора
---
```

### Архив (archive)
```yaml
---
title: "Archives"
type: "archive"
---
```

### Главная страница (index)
```yaml
---
title: "Welcome"
type: "index"
---
```

## Примеры URL

1. **Страница**:
   - Метаданные: `category: "about"`
   - URL: `/about/team`
   - Файл: `public/about/team/index.html`

2. **Пост**:
   - Метаданные: `category: "programming/python"`
   - URL: `/programming/python/getting-started`
   - Файл: `public/programming/python/getting-started/index.html`

3. **Тег**:
   - Метаданные: `name: "python"`
   - URL: `/python`
   - Файл: `public/python/index.html`

4. **Категория**:
   - Метаданные: `category_path: "programming/python"`
   - URL: `/programming/python`
   - Файл: `public/programming/python/index.html`

5. **Автор**:
   - Метаданные: `name: "john-doe"`
   - URL: `/john-doe`
   - Файл: `public/john-doe/index.html`

6. **Архив**:
   - URL: `/archives`
   - Файл: `public/archives/index.html`

7. **Главная**:
   - URL: `/`
   - Файл: `public/index.html`

## Особенности

1. **Clean URLs**:
   - Все URL генерируются без расширения `.html`
   - Файлы сохраняются как `index.html` в соответствующих директориях

2. **Структура директорий**:
   - Структура файлов в `content/` не влияет на финальные URL
   - URL определяются метаданными в файлах

3. **Многоязычность**:
   - Поддерживается префикс языка в URL
   - Например: `/en/about/team` или `/ru/about/team`

4. **Категории**:
   - Поддерживают иерархическую структуру
   - Путь категории может содержать подкатегории

## Настройка

Маршрутизацию можно настроить в конфигурационном файле:

```toml
[router]
URL_PATTERNS = { "page" = "custom/{category}/{slug}" }
SAVE_AS_PATTERNS = { "page" = "custom/{category}/{slug}/index.html" }
USE_LANGUAGE_PREFIXES = true
EXCLUDE_DEFAULT_LANG_PREFIX = true
default_language = "en"
```

## Best Practices

1. Используйте осмысленные категории и пути
2. Избегайте длинных URL
3. Используйте clean URLs без расширений
4. Поддерживайте единообразие в структуре URL
5. Учитывайте SEO при проектировании URL
6. Используйте иерархические категории для организации контента 