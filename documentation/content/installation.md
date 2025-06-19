---
title: Установка
date: 2025-05-20
author: nestessia
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

## Проверка установки

После установки проверьте, что StaticFlow доступен:

```bash
staticflow --version
```

## Обновление

Для обновления до последней версии:

```bash
pip install --upgrade staticflow
```

## Установка на Windows

1. Скачайте и установите Python с официального сайта: https://www.python.org/downloads/
   - При установке обязательно выберите опцию "Add Python to PATH".
2. Откройте командную строку (Win+R → cmd).
3. Проверьте версию Python и pip:
   ```bash
   python --version
   pip --version
   ```
4. Установите StaticFlow:
   ```bash
   pip install staticflow
   ```
5. Запустите StaticFlow:
   ```bash
   staticflow --version
   ```

## Установка на Ubuntu

1. Обновите пакеты:
   ```bash
   sudo apt update && sudo apt upgrade
   ```
2. Установите Python и pip:
   ```bash
   sudo apt install python3 python3-pip
   ```
3. Проверьте версию Python:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Установите StaticFlow:
   ```bash
   pip3 install staticflow
   ```
5. Запустите StaticFlow:
   ```bash
   staticflow --version
   ```

## Установка на macOS

1. Убедитесь, что установлен Homebrew (если нет — установите с https://brew.sh/):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Установите Python и pip:
   ```bash
   brew install python
   ```
3. Проверьте версию Python:
   ```bash
   python3 --version
   pip3 --version
   ```
4. Установите StaticFlow:
   ```bash
   pip3 install staticflow
   ```
5. Запустите StaticFlow:
   ```bash
   staticflow --version
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

- Проверьте [GitHub Issues](https://github.com/nestessia/StaticFlow-diploma/issues)

- Создайте новый issue с подробным описанием проблемы

