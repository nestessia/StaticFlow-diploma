#!/usr/bin/env python3
"""
Скрипт для публикации StaticFlow на PyPI
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, capture_output=True):
    """Выполнить команду и вернуть результат"""
    print(f"Выполняю: {command}")
    result = subprocess.run(
        command, shell=True, capture_output=capture_output, text=True
    )
    if check and result.returncode != 0:
        if capture_output:
            print(f"Ошибка: {result.stderr}")
        sys.exit(1)
    return result


def clean_build():
    """Очистить предыдущие сборки"""
    print("Очищаю предыдущие сборки...")
    dirs_to_clean = ["build", "dist", "*.egg-info"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Удален: {dir_name}")


def build_package():
    """Собрать пакет"""
    print("Собираю пакет...")
    run_command("python -m build")


def check_package():
    """Проверить пакет"""
    print("Проверяю пакет...")
    run_command("python -m twine check dist/*")


def setup_pypirc():
    """Настроить файл .pypirc в домашней директории"""
    home_dir = Path.home()
    pypirc_path = home_dir / ".pypirc"
    
    # Если файл .pypirc уже существует в домашней директории, не трогаем его
    if pypirc_path.exists():
        print(f"Файл .pypirc уже существует в {pypirc_path}")
        return
    
    # Если файл .pypirc существует в корне проекта, копируем его
    project_pypirc = Path(".pypirc")
    if project_pypirc.exists():
        print(f"Копирую .pypirc из проекта в {pypirc_path}")
        shutil.copy2(project_pypirc, pypirc_path)
        # Устанавливаем правильные права доступа
        pypirc_path.chmod(0o600)
    else:
        print("Предупреждение: файл .pypirc не найден ни в проекте, "
              "ни в домашней директории")


def upload_to_pypi():
    """Загрузить на PyPI"""
    print("Загружаю на PyPI...")
    
    # Настраиваем .pypirc перед загрузкой
    setup_pypirc()
    
    # Проверяем, есть ли переменные окружения для аутентификации
    if os.getenv('TWINE_USERNAME') and os.getenv('TWINE_PASSWORD'):
        print("Использую переменные окружения для аутентификации")
        command = "python -m twine upload dist/*"
    else:
        print("Использую файл .pypirc для аутентификации")
        command = "python -m twine upload dist/*"
    
    # Не перехватываем вывод для интерактивных команд
    run_command(command, capture_output=False)


def check_dependencies():
    """Проверить наличие необходимых зависимостей"""
    import importlib
    
    try:
        importlib.import_module('twine')
        print("✓ twine установлен")
    except ImportError:
        print("✗ twine не установлен. Установите: pip install twine")
        sys.exit(1)
    
    try:
        importlib.import_module('build')
        print("✓ build установлен")
    except ImportError:
        print("✗ build не установлен. Установите: pip install build")
        sys.exit(1)


def main():
    """Основная функция"""
    if len(sys.argv) < 2:
        print("Использование: python scripts/publish.py prod")
        print("  prod - загрузить на PyPI")
        sys.exit(1)

    target = sys.argv[1]

    # Проверяем зависимости
    check_dependencies()

    # Проверяем, что мы в корневой директории проекта
    if not os.path.exists("pyproject.toml"):
        print("Ошибка: pyproject.toml не найден. "
              "Запустите скрипт из корневой директории проекта.")
        sys.exit(1)

    # Очищаем предыдущие сборки
    clean_build()
    build_package()
    check_package()

    if target == "prod":
        upload_to_pypi()
        print("Пакет успешно загружен на PyPI!")
        print("Для установки: pip install staticflow")
    else:
        print("Неизвестная цель. Используйте 'prod'")
        sys.exit(1)


if __name__ == "__main__":
    main()
