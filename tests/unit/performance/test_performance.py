import unittest
import time
import psutil
import tempfile
from pathlib import Path
import requests
from staticflow.core import Config, Engine
from staticflow.core.builder import Builder, validate_project_structure
from staticflow.core.server import Server
import threading
from concurrent.futures import ThreadPoolExecutor
import asyncio
import toml
from aiohttp import web
import os


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Создаем необходимые директории
        self.content_dir = Path(self.temp_dir) / 'content'
        self.templates_dir = Path(self.temp_dir) / 'templates'
        self.static_dir = Path(self.temp_dir) / 'static'
        self.output_dir = Path(self.temp_dir) / 'output'
        
        dirs = [
            self.content_dir,
            self.templates_dir,
            self.static_dir,
            self.output_dir
        ]
        for directory in dirs:
            directory.mkdir(parents=True)
        
        # Создаем базовый шаблон
        template_path = self.templates_dir / 'page.html'
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    {{ content }}
</body>
</html>
            """)
        
        # Создаем конфигурационный файл
        config_data = {
            'site_name': 'Test Site',
            'site_description': 'Test site for performance testing',
            'base_url': 'http://localhost:8000',
            'source_dir': str(self.content_dir),
            'output_dir': str(self.output_dir),
            'template_dir': str(self.templates_dir),
            'static_dir': str(self.static_dir),
            'static_url': '/static',
            'languages': ['en'],
            'default_language': 'en'
        }
        
        config_path = Path(self.temp_dir) / 'config.toml'
        with open(config_path, 'w', encoding='utf-8') as f:
            toml.dump(config_data, f)
        
        self.config = Config(config_path)
        self.engine = Engine(self.config)
        self.builder = Builder(self.config, self.engine)
        self.server = Server(self.config, self.engine, dev_mode=True)
        self.process = psutil.Process()

    def tearDown(self):
        # Очистка временных файлов
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def create_test_page(self, filename, title, content):
        """Создает тестовую страницу с заданными параметрами."""
        page_path = self.content_dir / filename
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: {title}
template: page.html
---

{content}
""")
        return page_path

    def validate_and_build(self):
        """Проверяет структуру проекта и выполняет сборку."""
        errors, warnings = validate_project_structure(self.config)
        if errors:
            self.fail("Ошибки в структуре проекта:\n" + "\n".join(errors))
        if warnings:
            print("Предупреждения:", "\n".join(warnings))
        self.builder.build()

    def test_build_time(self):
        """Тест времени сборки сайта (≤30 секунд для 1000 страниц)"""
        # Создаем тестовые страницы
        for i in range(1000):
            self.create_test_page(
                f"page_{i}.md",
                f"Page {i}",
                f"# Page {i}\n\nTest content for page {i}"
            )
        
        start_time = time.time()
        self.validate_and_build()
        build_time = time.time() - start_time
        
        self.assertLessEqual(
            build_time, 30,
            f"Время сборки ({build_time:.2f} сек) превышает "
            f"допустимое (30 сек)"
        )

    def test_dev_server_response_time(self):
        """Тест времени отклика сервера разработки (≤100 мс)"""
        # Создаем тестовую страницу
        self.create_test_page(
            "index.md",
            "Test Page",
            "# Test Page\n\nTest content"
        )
        
        self.validate_and_build()
        
        # Запускаем сервер в отдельном потоке
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_server():
            runner = web.AppRunner(self.server.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', 8000)
            await site.start()
            return runner
        
        server_runner = loop.run_until_complete(run_server())
        
        try:
            time.sleep(1)  # Даем серверу время на запуск
            
            start_time = time.time()
            requests.get("http://localhost:8000")
            response_time = (time.time() - start_time) * 1000
            
            self.assertLessEqual(
                response_time, 100,
                f"Время отклика сервера ({response_time:.2f} мс) "
                f"превышает допустимое (100 мс)"
            )
        finally:
            # Корректно останавливаем сервер
            async def cleanup():
                await server_runner.cleanup()
            
            loop.run_until_complete(cleanup())
            loop.close()

    def test_page_load_time(self):
        """Тест времени загрузки страницы (≤2 секунды)"""
        # Создаем тестовую страницу
        self.create_test_page(
            "test_page.md",
            "Test Page",
            "# Test Page\n\nTest content"
        )
        
        self.validate_and_build()
        
        # Запускаем сервер в отдельном потоке
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_server():
            runner = web.AppRunner(self.server.app)
            await runner.setup()
            site = web.TCPSite(runner, 'localhost', 8000)
            await site.start()
            return runner
        
        server_runner = loop.run_until_complete(run_server())
        
        try:
            time.sleep(1)  # Даем серверу время на запуск
            
            start_time = time.time()
            requests.get("http://localhost:8000/test_page")
            load_time = time.time() - start_time
            
            self.assertLessEqual(
                load_time, 2,
                f"Время загрузки страницы ({load_time:.2f} сек) "
                f"превышает допустимое (2 сек)"
            )
        finally:
            # Корректно останавливаем сервер
            async def cleanup():
                await server_runner.cleanup()
            
            loop.run_until_complete(cleanup())
            loop.close()

    def test_content_file_processing_time(self):
        """Тест времени обработки файла контента (≤50 мс)"""
        test_file = self.create_test_page(
            "test.md",
            "Test Content",
            "# Test Content\n\nTest content with some markdown"
        )
        
        start_time = time.time()
        self.engine._process_page(test_file)
        processing_time = (time.time() - start_time) * 1000
        
        self.assertLessEqual(
            processing_time, 50,
            f"Время обработки файла ({processing_time:.2f} мс) "
            f"превышает допустимое (50 мс)"
        )

    def test_memory_usage(self):
        """Тест использования памяти (≤500 МБ)"""
        # Создаем тестовые страницы для нагрузки
        for i in range(100):
            self.create_test_page(
                f"page_{i}.md",
                f"Page {i}",
                f"# Page {i}\n\n{'Test content ' * 1000}"
            )
        
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        self.validate_and_build()
        final_memory = self.process.memory_info().rss / 1024 / 1024
        memory_usage = final_memory - initial_memory
        
        self.assertLessEqual(
            memory_usage, 500,
            f"Использование памяти ({memory_usage:.2f} МБ) "
            f"превышает допустимое (500 МБ)"
        )

    def test_cpu_usage(self):
        """Тест использования CPU (≤80%)"""
        def monitor_cpu():
            cpu_percentages = []
            while not self.stop_monitoring:
                cpu_percentages.append(self.process.cpu_percent())
                time.sleep(0.1)
            return max(cpu_percentages) if cpu_percentages else 0

        self.stop_monitoring = False
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Создаем нагрузку
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for i in range(100):
                test_file = self.create_test_page(
                    f"page_{i}.md",
                    f"Page {i}",
                    f"# Page {i}\n\n{'Test content ' * 1000}"
                )
                futures.append(
                    executor.submit(
                        self.engine._process_page,
                        test_file
                    )
                )
            
            for future in futures:
                future.result()
        
        self.stop_monitoring = True
        monitor_thread.join()
        max_cpu_usage = monitor_thread.result()
        
        self.assertLessEqual(
            max_cpu_usage, 80,
            f"Использование CPU ({max_cpu_usage:.2f}%) "
            f"превышает допустимое (80%)"
        )


if __name__ == '__main__':
    unittest.main()
