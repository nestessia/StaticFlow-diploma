---
title: Быстрый старт
date: 2024-03-20
author: nastya
tags: [quickstart, tutorial, basics]
format: markdown
template: page.html
---

# Быстрый старт с StaticFlow

Это руководство поможет вам быстро начать работу с StaticFlow. Мы создадим простой сайт-блог с основными функциями.

## Создание проекта

1. Создайте новый проект:

```bash
staticflow new my-blog
cd my-blog
```

2. Запустите сервер разработки:

```bash
staticflow serve
```

## Структура проекта

После создания проекта у вас будет следующая структура:

```
my-blog/
├── content/          # Контент сайта
│   └── index.md     # Главная страница
├── templates/        # Шаблоны
│   ├── base.html    # Базовый шаблон
│   └── page.html    # Шаблон страницы
├── static/          # Статические файлы
│   ├── css/        # Стили
│   └── js/         # Скрипты
└── config.toml      # Конфигурация
```

## Создание первой страницы

1. Откройте `content/index.md` и отредактируйте его:

```markdown
---
title: Мой блог
date: 2024-03-20
author: nastya
tags: [blog, welcome]
format: markdown
template: page.html
---

# Добро пожаловать в мой блог!

Это моя первая страница, созданная с помощью StaticFlow.
```

## Добавление поста

1. Создайте новый файл `content/posts/my-first-post.md`:

```markdown
---
title: Мой первый пост
date: 2024-03-20
author: nastya
tags: [blog, first-post]
format: markdown
template: post.html
---

# Мой первый пост

Это мой первый пост в блоге. Здесь я буду делиться своими мыслями и идеями.
```

## Настройка шаблона

1. Откройте `templates/base.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }} - {{ config.site_name }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <a href="/">Главная</a>
            <a href="/posts">Посты</a>
        </nav>
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        <p>&copy; {{ config.site_name }} {{ now.year }}</p>
    </footer>
</body>
</html>
```

## Добавление стилей

1. Создайте файл `static/css/style.css`:

```css
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
}

header {
    margin-bottom: 20px;
}

nav a {
    margin-right: 10px;
}
```

## Сборка сайта

Для сборки сайта выполните:

```bash
staticflow build
```

Собранный сайт будет находиться в директории `output/`.

## Следующие шаги

Теперь, когда у вас есть базовый сайт, вы можете:

1. Добавить больше страниц и постов
2. Настроить категории и теги
3. Добавить пользовательские шаблоны
4. Интегрировать плагины
5. Настроить поиск
6. Добавить комментарии

## Полезные команды

- `staticflow serve` - запуск сервера разработки
- `staticflow build` - сборка сайта
- `staticflow clean` - очистка директории output
- `staticflow new-page` - создание новой страницы
- `staticflow new-post` - создание нового поста

## Дополнительные ресурсы

- [Документация по шаблонам](templates.html)
- [Руководство по контенту](content.html)
- [Список плагинов](plugins.html)
- [API документация](api.html)