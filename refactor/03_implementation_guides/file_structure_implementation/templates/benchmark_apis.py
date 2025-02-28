#!/usr/bin/env python
"""
API Benchmarking Script for Vidst

This script benchmarks the performance of various API integrations used in the Vidst project.
It measures latency, throughput, error rates, and costs for each API under different load conditions.

Usage:
    python benchmark_apis.py [--api API_NAME] [--iterations ITERATIONS] [--concurrency CONCURRENCY]

Options:
    --api API_NAME            API to benchmark (twelve_labs, pinecone, document_ai, all)
    --iterations ITERATIONS   Number of API calls to make for each test (default: 100)
    --concurrency CONCURRENCY Number of concurrent requests (default: 10)
    --verbose                 Enable verbose output
    --output-file FILE        Path to save results (default: benchmark_results.json)
    --help                    Show this help message and exit
"""

import argparse
import asyncio
import time
import json
import logging
import statistics
import sys
from typing import Dict, List, Any, Optional, Callable, Union
import aiohttp
from functools import wraps
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_benchmarks.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("api_benchmarks")


def timing_decorator(func):
    """Decorator to measure execution time of a function."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            status = "success"
        except Exception as e:
            result = None
            status = f"error: {str(e)}"
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            logger.debug(f"{func.__name__} completed in {duration:.4f}s with status: {status}")
        return result, duration
    return wrapper


class APIBenchmark:
    """Base class for API benchmarking."""
    
    def __init__(
        self,
        name: str,
        iterations: int = 100,
        concurrency: int = 10,
        verbose: bool = False
    ):
        """Initialize API benchmark.
        
        Args:
            name: Name of the API
            iterations: Number of API calls to make
            concurrency: Number of concurrent requests
            verbose: Whether to print verbose output
        """
        self.name = name
        self.iterations = iterations
        self.concurrency = concurrency
        self.verbose = verbose
        self.session = None
        self.results = {
            "api_name": name,
            "iterations": iterations,
            "concurrency": concurrency,
            "latencies": [],
            "errors": 0,
            "throughput": 0,
            "cost_estimate": 0,
            "timestamp": time.time()
        }
        
        logger.info(f"Initializing benchmark for {name} API")
        logger.info(f"  Iterations: {iterations}")
        logger.info(f"  Concurrency: {concurrency}")
    
    async def setup(self):
        """Set up resources for benchmarking."""
        self.session = aiohttp.ClientSession()
        logger.info(f"Set up resources for {self.name} API")
    
    async def cleanup(self):
        """Clean up resources after benchmarking."""
        if self.session:
            await self.session.close()
        logger.info(f"Cleaned up resources for {self.name} API")
    
    async def run_benchmark(self) -> Dict[str, Any]:
        """Run the benchmark.
        
        Returns:
            Dictionary with benchmark results
        """
        try:
            await self.setup()
            
            start_time = time.time()
            
            # Create a list of tasks
            tasks = []
            for i in range(self.iterations):
                tasks.append(self.make_api_call(i))
            
            # Run tasks with limited concurrency
            semaphore = asyncio.Semaphore(self.concurrency)
            
            async def bounded_api_call(i):
                async with semaphore:
                    return await tasks[i]
            
            # Execute all tasks
            results = await asyncio.gather(
                *[bounded_api_call(i) for i in range(self.iterations)],
                return_exceptions=True
            )
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.results["errors"] += 1
                    logger.warning(f"API call error: {str(result)}")
                else:
                    _, duration = result
                    self.results["latencies"].append(duration)
            
            # Calculate statistics
            end_time = time.time()
            total_duration = end_time - start_time
            
            if self.results["latencies"]:
                self.results["min_latency"] = min(self.results["latencies"])
                self.results["max_latency"] = max(self.results["latencies"])
                self.results["avg_latency"] = statistics.mean(self.results["latencies"])
                self.results["median_latency"] = statistics.median(self.results["latencies"])
                self.results["p95_latency"] = self._percentile(self.results["latencies"], 95)
                self.results["p99_latency"] = self._percentile(self.results["latencies"], 99)
            
            self.results["throughput"] = self.iterations / total_duration
            self.results["total_duration"] = total_duration
            self.results["success_rate"] = (self.iterations - self.results["errors"]) / self.iterations
            
            # Estimate cost (implement in subclasses)
            self.results["cost_estimate"] = self._estimate_cost()
            
            logger.info(f"Benchmark for {self.name} API completed")
            logger.info(f"  Avg latency: {self.results.get('avg_latency', 0):.4f}s")
            logger.info(f"  Throughput: {self.results['throughput']:.2f} requests/second")
            logger.info(f"  Success rate: {self.results['success_rate']:.2%}")
            
            return self.results
            
        finally:
            await self.cleanup()
    
    async def make_api_call(self, iteration: int) -> Any:
        """Make an API call for benchmarking.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            API call result and duration tuple
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement make_api_call")
    
    def _estimate_cost(self) -> float:
        """Estimate the cost of API calls.
        
        Returns:
            Estimated cost in USD
        """
        return 0.0  # Override in subclasses
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate a percentile from the data.
        
        Args:
            data: List of values
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Percentile value
        """
        size = len(data)
        if not size:
            return 0
        
        sorted_data = sorted(data)
        idx = (size * percentile) // 100
        return sorted_data[idx]


class TwelveLabsBenchmark(APIBenchmark):
    """Benchmark for Twelve Labs API."""
    
    def __init__(self, *args, **kwargs):
        """Initialize Twelve Labs benchmark."""
        super().__init__("twelve_labs", *args, **kwargs)
        self.api_key = self._get_api_key()
        self.test_videos = self._load_test_videos()
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable."""
        # In actual implementation, get from environment or config
        return "your_twelve_labs_api_key"
    
    def _load_test_videos(self) -> List[str]:
        """Load test video IDs.
        
        Returns:
            List of video IDs for testing
        """
        # In actual implementation, load from a file or database
        return ["video_id_1", "video_id_2", "video_id_3"]
    
    @timing_decorator
    async def make_api_call(self, iteration: int) -> Any:
        """Make a Twelve Labs API call.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            API call result
        """
        # Select a random test video
        video_id = random.choice(self.test_videos)
        
        # Simulate different API operations based on iteration
        op_type = iteration % 3
        
        if op_type == 0:
            # Scene detection
            return await self._call_scene_detection(video_id)
        elif op_type == 1:
            # Semantic search
            return await self._call_semantic_search(video_id)
        else:
            # Video metadata
            return await self._call_video_metadata(video_id)
    
    async def _call_scene_detection(self, video_id: str) -> Any:
        """Call Twelve Labs scene detection API.
        
        Args:
            video_id: ID of the video
            
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate API response
        return {
            "video_id": video_id,
            "scenes": [
                {"start_time": 0, "end_time": 15.5},
                {"start_time": 15.5, "end_time": 42.1},
                {"start_time": 42.1, "end_time": 67.8}
            ]
        }
    
    async def _call_semantic_search(self, video_id: str) -> Any:
        """Call Twelve Labs semantic search API.
        
        Args:
            video_id: ID of the video
            
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.3, 1.5))
        
        # Simulate API response
        return {
            "query": "person walking",
            "results": [
                {"video_id": video_id, "start_time": 12.3, "score": 0.92},
                {"video_id": video_id, "start_time": 45.7, "score": 0.87}
            ]
        }
    
    async def _call_video_metadata(self, video_id: str) -> Any:
        """Call Twelve Labs video metadata API.
        
        Args:
            video_id: ID of the video
            
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.1, 0.8))
        
        # Simulate API response
        return {
            "video_id": video_id,
            "duration": 120.5,
            "format": "mp4",
            "resolution": "1920x1080"
        }
    
    def _estimate_cost(self) -> float:
        """Estimate the cost of Twelve Labs API calls.
        
        Returns:
            Estimated cost in USD
        """
        # Example pricing: $0.01 per API call
        # Adjust based on actual pricing
        return self.iterations * 0.01


class PineconeBenchmark(APIBenchmark):
    """Benchmark for Pinecone API."""
    
    def __init__(self, *args, **kwargs):
        """Initialize Pinecone benchmark."""
        super().__init__("pinecone", *args, **kwargs)
        self.api_key = self._get_api_key()
        self.index_name = "vidst-vectors"
        self.test_vectors = self._generate_test_vectors()
    
    def _get_api_key(self) -> str:
        """Get API key from environment variable."""
        # In actual implementation, get from environment or config
        return "your_pinecone_api_key"
    
    def _generate_test_vectors(self) -> List[Dict[str, Any]]:
        """Generate test vectors for benchmarking.
        
        Returns:
            List of test vectors
        """
        vectors = []
        dimension = 512  # Example dimension
        
        for i in range(10):  # Generate 10 test vectors
            vectors.append({
                "id": f"test_vector_{i}",
                "values": [random.random() for _ in range(dimension)],
                "metadata": {
                    "source": f"benchmark_test_{i}",
                    "timestamp": time.time()
                }
            })
        
        return vectors
    
    @timing_decorator
    async def make_api_call(self, iteration: int) -> Any:
        """Make a Pinecone API call.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            API call result
        """
        # Select operation type based on iteration
        op_type = iteration % 3
        
        if op_type == 0:
            # Vector search
            return await self._call_vector_search()
        elif op_type == 1:
            # Vector upsert
            return await self._call_vector_upsert()
        else:
            # Vector delete
            return await self._call_vector_delete()
    
    async def _call_vector_search(self) -> Any:
        """Call Pinecone vector search API.
        
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.05, 0.3))
        
        # Simulate API response
        return {
            "matches": [
                {"id": "vector_1", "score": 0.92, "metadata": {"source": "video_1"}},
                {"id": "vector_2", "score": 0.87, "metadata": {"source": "video_2"}},
                {"id": "vector_3", "score": 0.81, "metadata": {"source": "video_3"}}
            ]
        }
    
    async def _call_vector_upsert(self) -> Any:
        """Call Pinecone vector upsert API.
        
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.1, 0.4))
        
        # Select a random test vector
        vector = random.choice(self.test_vectors)
        
        # Simulate API response
        return {
            "upsertedCount": 1
        }
    
    async def _call_vector_delete(self) -> Any:
        """Call Pinecone vector delete API.
        
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.05, 0.2))
        
        # Select a random test vector ID
        vector_id = random.choice(self.test_vectors)["id"]
        
        # Simulate API response
        return {
            "deletedCount": 1
        }
    
    def _estimate_cost(self) -> float:
        """Estimate the cost of Pinecone API calls.
        
        Returns:
            Estimated cost in USD
        """
        # Example pricing: $0.002 per 1000 API calls
        # Adjust based on actual pricing
        return (self.iterations / 1000) * 0.002


class DocumentAIBenchmark(APIBenchmark):
    """Benchmark for Google Document AI API."""
    
    def __init__(self, *args, **kwargs):
        """Initialize Document AI benchmark."""
        super().__init__("document_ai", *args, **kwargs)
        self.project_id = "your-project-id"
        self.location = "us-central1"
        self.processor_id = "your-processor-id"
        self.test_images = self._load_test_images()
    
    def _load_test_images(self) -> List[str]:
        """Load test image paths.
        
        Returns:
            List of test image paths
        """
        # In actual implementation, load from a directory
        return ["image_1.jpg", "image_2.jpg", "image_3.jpg"]
    
    @timing_decorator
    async def make_api_call(self, iteration: int) -> Any:
        """Make a Document AI API call.
        
        Args:
            iteration: Current iteration number
            
        Returns:
            API call result
        """
        # Select a random test image
        image_path = random.choice(self.test_images)
        
        # Simulate API call
        return await self._call_document_processing(image_path)
    
    async def _call_document_processing(self, image_path: str) -> Any:
        """Call Document AI processing API.
        
        Args:
            image_path: Path to the image
            
        Returns:
            API call result
        """
        # Simulate API call with random delay
        await asyncio.sleep(random.uniform(0.8, 2.5))
        
        # Simulate API response
        return {
            "document": {
                "text": "Sample text extracted from the image",
                "pages": [
                    {
                        "page_number": 1,
                        "dimension": {"width": 800, "height": 600},
                        "blocks": [
                            {
                                "text": "Sample text block",
                                "confidence": 0.95,
                                "bounding_box": [(10, 10), (100, 10), (100, 50), (10, 50)]
                            }
                        ]
                    }
                ]
            }
        }
    
    def _estimate_cost(self) -> float:
        """Estimate the cost of Document AI API calls.
        
        Returns:
            Estimated cost in USD
        """
        # Example pricing: $0.05 per page
        # Adjust based on actual pricing
        return self.iterations * 0.05


async def run_benchmarks(args) -> Dict[str, Any]:
    """Run benchmarks based on command-line arguments.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Dictionary with benchmark results
    """
    results = {}
    
    # Determine which APIs to benchmark
    apis_to_benchmark = []
    if args.api == "all":
        apis_to_benchmark = ["twelve_labs", "pinecone", "document_ai"]
    else:
        apis_to_benchmark = [args.api]
    
    # Run benchmarks for selected APIs
    for api_name in apis_to_benchmark:
        logger.info(f"Starting benchmark for {api_name} API")
        
        if api_name == "twelve_labs":
            benchmark = TwelveLabsBenchmark(
                iterations=args.iterations,
                concurrency=args.concurrency,
                verbose=args.verbose
            )
        elif api_name == "pinecone":
            benchmark = PineconeBenchmark(
                iterations=args.iterations,
                concurrency=args.concurrency,
                verbose=args.verbose
            )
        elif api_name == "document_ai":
            benchmark = DocumentAIBenchmark(
                iterations=args.iterations,
                concurrency=args.concurrency,
                verbose=args.verbose
            )
        else:
            logger.warning(f"Unknown API: {api_name}")
            continue
        
        try:
            api_results = await benchmark.run_benchmark()
            results[api_name] = api_results
        except Exception as e:
            logger.error(f"Error running benchmark for {api_name}: {str(e)}")
            results[api_name] = {"error": str(e)}
    
    return results


def main():
    """Main function to run the API benchmarks."""
    parser = argparse.ArgumentParser(description="Benchmark APIs for Vidst")
    parser.add_argument(
        "--api",
        choices=["twelve_labs", "pinecone", "document_ai", "all"],
        default="all",
        help="API to benchmark"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Number of API calls to make for each test"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Number of concurrent requests"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="benchmark_results.json",
        help="Path to save results"
    )
    
    args = parser.parse_args()
    
    # Run benchmarks
    results = asyncio.run(run_benchmarks(args))
    
    # Save results to file
    with open(args.output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Benchmark results saved to {args.output_file}")
    
    # Print summary
    print("\nBenchmark Summary:")
    for api_name, api_results in results.items():
        if "error" in api_results:
            print(f"  {api_name}: ERROR - {api_results['error']}")
        else:
            print(f"  {api_name}:")
            print(f"    Avg Latency: {api_results.get('avg_latency', 0):.4f}s")
            print(f"    Throughput: {api_results.get('throughput', 0):.2f} requests/second")
            print(f"    Success Rate: {api_results.get('success_rate', 0):.2%}")
            print(f"    Est. Cost: ${api_results.get('cost_estimate', 0):.4f}")


if __name__ == "__main__":
    main()
