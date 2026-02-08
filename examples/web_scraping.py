import time
import random
from adaptive_executor import AdaptiveExecutor, MultiCriterionPolicy
from adaptive_executor.criteria import TimeCriterion

def scrape_url(url):
    """Simulate web scraping with variable duration."""
    print(f"Scraping {url}")
    
    # Simulate network latency and processing time
    processing_time = random.uniform(0.5, 2.0)
    time.sleep(processing_time)
    
    # Simulate successful scrape
    data_size = random.randint(1000, 5000)
    print(f"  Scraped {data_size} bytes from {url} in {processing_time:.2f}s")
    
    return {
        'url': url,
        'size': data_size,
        'time': processing_time
    }

def main():
    print("=== Web Scraping with Time-Based Scaling ===")
    
    # Aggressive during off-peak hours, respectful during business hours
    time_policy = TimeCriterion(
        day_workers=2,      # Respectful during business hours
        night_workers=20,    # Aggressive during off-peak
        night_start=22,       # 10 PM to 6 AM is off-peak
        night_end=6,
        tz="America/New_York"
    )
    
    policy = MultiCriterionPolicy([time_policy], hard_cap=25)
    
    executor = AdaptiveExecutor(
        max_workers=30,
        policy=policy,
        check_interval=60  # Check every minute
    )
    
    # Generate URLs to scrape
    urls = [
        f"https://example.com/products/page/{i}"
        for i in range(1, 51)
    ]
    
    print(f"Current worker limit: {executor.current_limit}")
    print(f"Scraping {len(urls)} URLs...")
    
    start_time = time.time()
    
    # Submit all scraping tasks
    for url in urls:
        executor.submit(scrape_url, url)
    
    # Wait for completion
    executor.join()
    
    total_time = time.time() - start_time
    print(f"\nScraping completed in {total_time:.2f} seconds")
    print(f"Average time per URL: {total_time/len(urls):.2f}s")
    
    executor.shutdown()

if __name__ == "__main__":
    main()
