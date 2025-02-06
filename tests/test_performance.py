import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from staticflow.core.page import Page


def generate_test_content(content_dir: Path, count: int) -> None:
    """Generate test content files."""
    content_dir.mkdir(exist_ok=True)
    for i in range(count):
        file_path = content_dir / f"post-{i}.md"
        content = f"""---
title: Test Post {i}
date: 2024-02-06
---

# Test Post {i}

This is test post number {i}."""
        file_path.write_text(content)


def test_build_performance(engine, sample_content, temp_site_dir):
    """Test build performance with different content sizes."""
    # Set source and output directories
    engine.site.source_dir = sample_content
    engine.site.output_dir = temp_site_dir / "public"
    engine.site.output_dir.mkdir(exist_ok=True)
    
    results = []
    
    for file_count in [10, 50, 100]:
        # Generate test content
        generate_test_content(sample_content, file_count)
        
        # Measure build time
        start_time = time.time()
        engine.build()
        end_time = time.time()
        
        results.append({
            'file_count': file_count,
            'time': end_time - start_time,
            'files_per_second': file_count / (end_time - start_time)
        })
        
        # Print results
        print(f"\nBuild Performance ({file_count} files):")
        print(f"Time: {results[-1]['time']:.2f}s")
        print(f"Files/Second: {results[-1]['files_per_second']:.2f}")
        
    # Assert reasonable performance
    assert results[-1]['files_per_second'] > 10  # At least 10 files/s


def test_parallel_build_performance(engine, sample_content, temp_site_dir):
    """Test parallel build performance."""
    # Set source and output directories
    engine.site.source_dir = sample_content
    engine.site.output_dir = temp_site_dir / "public"
    engine.site.output_dir.mkdir(exist_ok=True)
    
    file_count = 100
    generate_test_content(sample_content, file_count)
    
    # Test different worker counts
    results = []
    for worker_count in [1, 2, 4, 8]:
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            # Simulate parallel processing
            chunks = [
                range(i, file_count, worker_count)
                for i in range(worker_count)
            ]
            
            def process_chunk(chunk):
                for i in chunk:
                    file_path = sample_content / f"post-{i}.md"
                    if file_path.exists():
                        # Create Page object from file
                        page = Page.from_file(file_path)
                        if page:
                            engine._process_page(page)
            
            list(executor.map(process_chunk, chunks))
            
        end_time = time.time()
        
        results.append({
            'worker_count': worker_count,
            'time': end_time - start_time,
            'files_per_second': file_count / (end_time - start_time)
        })
        
        # Print results
        print(f"\nParallel Build ({worker_count} workers):")
        print(f"Time: {results[-1]['time']:.2f}s")
        print(f"Files/Second: {results[-1]['files_per_second']:.2f}")
    
    # Assert performance improvement with parallelization
    assert results[-1]['files_per_second'] > results[0]['files_per_second']


@pytest.mark.asyncio
async def test_dev_server_performance(engine, async_client):
    """Test development server performance under load."""
    from staticflow.cli.server import DevServer
    
    # Set up directories
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    public_dir = Path("public")
    public_dir.mkdir(exist_ok=True)
    
    # Create test CSS file
    test_css = static_dir / "test.css"
    test_css.write_text("body { color: red; }")
    
    try:
        # Set up server
        server = DevServer(engine.config)
        client = await async_client(server.app)
        
        # Generate test requests
        async def make_requests(count):
            start_time = time.time()
            tasks = []
            
            for _ in range(count):
                # Only test static file serving
                tasks.append(client.get('/static/test.css'))
            
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            return {
                'request_count': len(tasks),
                'time': end_time - start_time,
                'requests_per_second': len(tasks) / (end_time - start_time),
                'success_rate': sum(
                    1 for r in responses if r.status == 200
                ) / len(responses)
            }
        
        # Test different load levels
        results = []
        for request_count in [10, 50, 100]:
            result = await make_requests(request_count)
            results.append(result)
            
            # Print results
            print(f"\nDev Server Performance ({request_count} requests):")
            print(f"Time: {result['time']:.2f}s")
            print(f"Requests/Second: {result['requests_per_second']:.2f}")
            print(f"Success Rate: {result['success_rate']*100:.1f}%")
        
        # Assert reasonable performance
        assert results[-1]['requests_per_second'] > 50  # At least 50 req/s
        assert results[-1]['success_rate'] > 0.95  # 95% success rate
    finally:
        # Cleanup
        test_css.unlink()
        static_dir.rmdir()
        if public_dir.exists():
            for file in public_dir.glob('*'):
                file.unlink()
            public_dir.rmdir()


@pytest.mark.asyncio
async def test_admin_panel_performance(engine, async_client):
    """Test admin panel performance under load."""
    from staticflow.admin import AdminPanel
    import shutil
    
    # Set up directories
    admin_static_dir = Path(__file__).parent.parent / 'staticflow/admin/static'
    admin_static_dir.mkdir(parents=True, exist_ok=True)
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    
    # Create test CSS file
    test_css = admin_static_dir / 'test.css'
    test_css.write_text('body { color: red; }')
    
    try:
        admin = AdminPanel(engine.config, engine)
        client = await async_client(admin.app)
        
        # Generate test data
        test_data = {
            'action': 'create',
            'path': 'test.md',
            'content': '# Test\n\nTest content.'
        }
        
        # Test API endpoint performance
        async def make_api_requests(count):
            start_time = time.time()
            tasks = []
            
            for _ in range(count):
                tasks.append(
                    client.post('/api/content', json=test_data)
                )
            
            responses = await asyncio.gather(*tasks)
            end_time = time.time()
            
            return {
                'request_count': len(tasks),
                'time': end_time - start_time,
                'requests_per_second': len(tasks) / (end_time - start_time),
                'success_rate': sum(
                    1 for r in responses if r.status == 200
                ) / len(responses)
            }
        
        # Test different load levels
        results = []
        for request_count in [5, 10, 20]:
            result = await make_api_requests(request_count)
            results.append(result)
            
            # Print results
            print(f"\nAdmin Panel Performance ({request_count} requests):")
            print(f"Time: {result['time']:.2f}s")
            print(f"Requests/Second: {result['requests_per_second']:.2f}")
            print(f"Success Rate: {result['success_rate']*100:.1f}%")
        
        # Assert reasonable performance
        assert results[-1]['requests_per_second'] > 10  # At least 10 req/s
        assert results[-1]['success_rate'] > 0.95  # 95% success rate
    finally:
        # Cleanup
        if admin_static_dir.exists():
            shutil.rmtree(admin_static_dir)
        if content_dir.exists():
            shutil.rmtree(content_dir) 