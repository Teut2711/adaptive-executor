import time
import random
from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import CpuCriterion, MemoryCriterion


def process_data_chunk(chunk_id, data_size):
    """Simulate processing a data chunk with CPU and memory usage."""
    print(f"Processing chunk {chunk_id} ({data_size} items)")

    # Simulate CPU-intensive processing
    processing_steps = data_size // 100
    for step in range(processing_steps):
        # Simulate computation
        _ = sum(range(100))
        time.sleep(0.01)

    # Simulate memory usage
    result_data = [random.random() for _ in range(data_size)]
    processed_count = len(result_data)

    print(f"  Processed {processed_count} items from chunk {chunk_id}")
    return {
        "chunk_id": chunk_id,
        "processed_count": processed_count,
        "processing_time": processing_steps * 0.01,
    }


def main():
    print("=== Data Processing with Resource-Aware Scaling ===")

    # Conservative scaling to protect system resources
    cpu_policy = CpuCriterion(threshold=70)  # Scale down when CPU > 70%
    memory_policy = MemoryCriterion(threshold=75)  # Scale down when memory > 75%

    policy = MultiCriterionPolicy(
        [cpu_policy, memory_policy], hard_cap=8  # Conservative limit
    )

    executor = AdaptiveExecutor(
        max_workers=12, policy=policy, check_interval=30  # Check every 30 seconds
    )

    # Simulate data chunks to process
    data_chunks = [
        {"chunk_id": i, "data_size": random.randint(500, 2000)} for i in range(20)
    ]

    total_items = sum(chunk["data_size"] for chunk in data_chunks)
    print(f"Current worker limit: {executor.current_limit}")
    print(f"Processing {len(data_chunks)} data chunks ({total_items} total items)...")

    start_time = time.time()
    results = []

    # Submit all processing tasks
    for chunk in data_chunks:
        future = executor.submit(
            process_data_chunk, chunk["chunk_id"], chunk["data_size"]
        )
        results.append(future)

    # Wait for completion
    executor.join()

    total_time = time.time() - start_time
    total_processed = sum(chunk["data_size"] for chunk in data_chunks)

    print(f"\nProcessing completed in {total_time:.2f} seconds")
    print(f"Total items processed: {total_processed}")
    print(f"Processing rate: {total_processed/total_time:.0f} items/second")

    executor.shutdown()


if __name__ == "__main__":
    main()
