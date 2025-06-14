---
title: Контент
date: 2024-03-20
author: nastya
tags: [content, markdown, front-matter]
format: markdown
template: page.html
---

# Работа с контентом

В этом разделе мы рассмотрим, как создавать и управлять контентом в StaticFlow.

## Форматы контента

StaticFlow поддерживает несколько форматов контента:

- Markdown (`.md`)
- HTML (`.html`)
- reStructuredText (`.rst`)
- Textile (`.textile`)

## Структура файлов контента

Каждый файл контента состоит из двух частей:

1. **Front Matter** - метаданные в формате YAML
2. **Содержимое** - основной контент в выбранном формате

### Пример файла

```markdown
---
title: Заголовок страницы
date: 2024-03-20
author: nastya
tags: [tag1, tag2]
category: blog
format: markdown
template: page.html
---

# Основной контент

Здесь идет содержимое страницы...
```

## Метаданные (Front Matter)

### Обязательные поля

- `title` - заголовок страницы
- `date` - дата создания/публикации
- `format` - формат контента

### Опциональные поля

- `author` - автор контента
- `tags` - список тегов
- `category` - категория
- `template` - используемый шаблон
- `draft` - черновик (true/false)
- `description` - описание страницы
- `image` - главное изображение
- `slug` - URL-friendly версия заголовка

## Организация контента

### Категории

Категории позволяют организовать контент иерархически:

```
content/
├── blog/
│   ├── index.md
│   ├── post-1.md
│   └── post-2.md
├── projects/
│   ├── index.md
│   └── project-1.md
└── about.md
```

### Теги

Теги помогают группировать контент по темам:

```markdown
---
tags: [python, web, tutorial]
---
```

## Специальные страницы

### Главная страница

Файл `content/index.md` используется как главная страница сайта.

### Страницы категорий

Создайте `index.md` в директории категории для создания страницы категории:

```markdown
---
title: Блог
template: category.html
---
```

### Страницы тегов

Теги автоматически генерируют страницы при использовании.

## Работа с медиафайлами

### Изображения

1. Поместите изображения в директорию `media/`
2. Используйте в контенте:

```markdown
![Описание](/media/image.jpg)
```

### Другие медиафайлы

- Видео
- Аудио
- PDF документы
- Другие файлы

## Шаблоны контента

### Страницы

```markdown
---
template: page.html
---
```

### Посты

```markdown
---
template: post.html
---
```

### Пользовательские шаблоны

Создайте свой шаблон в `templates/` и укажите его в front matter.

## Расширенный контент

### Математические формулы

```markdown
Inline формула: $E = mc^2$

Блочная формула:
$$
\int_0^\infty e^{-x} dx = 1
$$
```

### Диаграммы

```markdown
```mermaid
graph TD
A[Старт] --> B[Процесс]
B --> C{Условие}
C -->|Да| D[Результат 1]
C -->|Нет| E[Результат 2]
```
```

### Подсветка кода

```markdown
```python
def hello_world():
    print("Привет, StaticFlow!")
```
```

## Локализация

### Многоязычный контент

```markdown
---
language: ru
---

# Русский контент
```

```markdown
---
language: en
---

# English content
```

## Плагины для контента

- `staticflow-markdown` - расширенная поддержка Markdown
- `staticflow-images` - оптимизация изображений
- `staticflow-search` - поиск по контенту
- `staticflow-comments` - система комментариев 