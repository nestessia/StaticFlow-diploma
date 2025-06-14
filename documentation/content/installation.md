---
title: Установка
date: 2024-03-20
author: nastya
tags: [installation, setup, requirements]
format: markdown
template: page.html
---

# Установка StaticFlow

В этом разделе мы рассмотрим процесс установки StaticFlow и необходимые требования.

## Требования

Для работы StaticFlow требуется:

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (опционально, для работы с репозиториями)

## Установка через pip

Самый простой способ установить StaticFlow - использовать pip:

```bash
pip install staticflow
```

## Установка из исходного кода

Если вы хотите установить последнюю версию из репозитория:

```bash
git clone https://github.com/your-username/staticflow.git
cd staticflow
pip install -e .
```

## Проверка установки

После установки проверьте, что StaticFlow доступен:

```bash
staticflow --version
```

## Создание нового проекта

Чтобы создать новый проект:

```bash
staticflow new my-project
cd my-project
```

## Запуск сервера разработки

Для локальной разработки:

```bash
staticflow serve
```

Сайт будет доступен по адресу http://localhost:8000

## Обновление

Для обновления до последней версии:

```bash
pip install --upgrade staticflow
```

## Устранение неполадок

### Распространенные проблемы

1. **Ошибка "command not found"**
   - Убедитесь, что Python и pip установлены
   - Проверьте, что директория с исполняемыми файлами Python в PATH

2. **Проблемы с зависимостями**
   - Попробуйте создать новое виртуальное окружение
   - Обновите pip: `pip install --upgrade pip`

3. **Ошибки при сборке**
   - Проверьте версию Python
   - Убедитесь, что все зависимости установлены

### Получение помощи

Если у вас возникли проблемы:
- Проверьте [GitHub Issues](https://github.com/your-username/staticflow/issues)
- Задайте вопрос в [Discord сообществе](https://discord.gg/staticflow)
- Создайте новый issue с подробным описанием проблемы