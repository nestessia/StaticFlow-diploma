import pytest
import time
import asyncio
import aiohttp
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from staticflow.core.engine import Engine


def generate_test_content(content_dir: Path, count: int = 100):
    """Generate test content files."""
    for i in range(count):
        file_path = content_dir / f"post-{i}.md"
        content = f"""---
title: Test Post {i}
date: 2024-02-06
---
# Test Post {i}

This is test post number {i}.

## Section 1

Lorem ipsum dolor sit amet, consectetur adipiscing elit.
Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

## Section 2

Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris
nisi ut aliquip ex ea commodo consequat.

## Section 3

Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur.
"""
        file_path.write_text(content)


def test_build_performance(engine, sample_content, temp_site_dir):
    """Test build performance with different content sizes."""
    results = []
    
    for file_count in [10, 50, 100]:
        # Generate test content
        generate_test_content(sample_content, file_count)
        
        # Measure build time
        start_time = time.time()
        engine.build()
        end_time = time.time()
        
        build_time = end_time - start_time
        results.append({
            'file_count': file_count,
            'build_time': build_time,
            'files_per_second': file_count / build_time
        })
        
        # Clean up
        for file in sample_content.glob('post-*.md'):
            file.unlink()
            
    # Print results
    print("\nBuild Performance Results:")
    print("-------------------------")
    for result in results:
        print(f"Files: {result['file_count']}")
        print(f"Build Time: {result['build_time']:.2f}s")
        print(f"Files/Second: {result['files_per_second']:.2f}")
        print("-------------------------")
        
    # Assert reasonable performance
    assert results[-1]['files_per_second'] > 10  # At least 10 files per second


def test_parallel_build_performance(engine, sample_content, temp_site_dir):
    """Test parallel build performance."""
    file_count = 100
    generate_test_content(sample_content, file_count)
    
    # Test different worker counts
    results = []
    for worker_count in [1, 2, 4, 8]:
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            # Simulate parallel processing
            chunks = [range(i, file_count, worker_count) 
                     for i in range(worker_count)]
            
            def process_chunk(chunk):
                for i in chunk:
                    file_path = sample_content / f"post-{i}.md"
                    if file_path.exists():
                        engine.process_file(file_path)
                        
            list(executor.map(process_chunk, chunks))
        
        end_time = time.time()
        build_time = end_time - start_time
        
        results.append({
            'workers': worker_count,
            'build_time': build_time,
            'files_per_second': file_count / build_time
        })
    
    # Print results
    print("\nParallel Build Performance Results:")
    print("----------------------------------")
    for result in results:
        print(f"Workers: {result['workers']}")
        print(f"Build Time: {result['build_time']:.2f}s")
        print(f"Files/Second: {result['files_per_second']:.2f}")
        print("----------------------------------")
    
    # Assert parallel processing improves performance
    assert results[-1]['build_time'] < results[0]['build_time']


@pytest.mark.asyncio
async def test_dev_server_performance(engine, aiohttp_client):
    """Test development server performance under load."""
    from staticflow.cli.server import DevServer
    
    # Start server
    server = DevServer(engine.config)
    client = await aiohttp_client(server.app)
    
    # Generate test requests
    async def make_requests(count):
        start_time = time.time()
        tasks = []
        
        for _ in range(count):
            tasks.append(client.get('/'))
            tasks.append(client.get('/_dev/events'))
            
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        return {
            'request_count': len(tasks),
            'time': end_time - start_time,
            'requests_per_second': len(tasks) / (end_time - start_time),
            'success_rate': sum(1 for r in responses 
                              if r.status == 200) / len(responses)
        }
    
    # Test different load levels
    results = []
    for request_count in [10, 50, 100]:
        result = await make_requests(request_count)
        results.append(result)
    
    # Print results
    print("\nDev Server Performance Results:")
    print("------------------------------")
    for result in results:
        print(f"Requests: {result['request_count']}")
        print(f"Time: {result['time']:.2f}s")
        print(f"Requests/Second: {result['requests_per_second']:.2f}")
        print(f"Success Rate: {result['success_rate']*100:.1f}%")
        print("------------------------------")
    
    # Assert reasonable performance
    assert results[-1]['requests_per_second'] > 50  # At least 50 req/s
    assert results[-1]['success_rate'] > 0.95  # 95% success rate


@pytest.mark.asyncio
async def test_admin_panel_performance(engine, aiohttp_client):
    """Test admin panel performance under load."""
    from staticflow.admin import AdminPanel
    
    admin = AdminPanel(engine.config, engine)
    client = await aiohttp_client(admin.app)
    
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
            tasks.append(client.post('/api/content', json=test_data))
            
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        
        return {
            'request_count': len(tasks),
            'time': end_time - start_time,
            'requests_per_second': len(tasks) / (end_time - start_time),
            'success_rate': sum(1 for r in responses 
                              if r.status == 200) / len(responses)
        }
    
    # Test different load levels
    results = []
    for request_count in [5, 10, 20]:
        result = await make_api_requests(request_count)
        results.append(result)
    
    # Print results
    print("\nAdmin Panel Performance Results:")
    print("-------------------------------")
    for result in results:
        print(f"Requests: {result['request_count']}")
        print(f"Time: {result['time']:.2f}s")
        print(f"Requests/Second: {result['requests_per_second']:.2f}")
        print(f"Success Rate: {result['success_rate']*100:.1f}%")
        print("-------------------------------")
    
    # Assert reasonable performance
    assert results[-1]['requests_per_second'] > 10  # At least 10 req/s
    assert results[-1]['success_rate'] > 0.95  # 95% success rate 