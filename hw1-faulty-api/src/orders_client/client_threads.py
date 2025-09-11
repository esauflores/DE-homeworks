import time
import httpx
import csv
from loguru import logger
from ratelimit import limits, sleep_and_retry
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINT = "http://localhost:8000/item/{}"
MAX_WORKERS = 12
RATE_LIMIT = 18
MAX_RETRIES = 5


@sleep_and_retry
@limits(calls=RATE_LIMIT, period=1)
def fetch_item(item_id):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = httpx.get(ENDPOINT.format(item_id), timeout=5)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                time.sleep(retry_after)
                retries += 1
            elif 500 <= response.status_code < 600:
                logger.warning(
                    f"Server error {response.status_code} for item {item_id}, retrying..."
                )
                time.sleep(1)
                retries += 1
            elif 400 <= response.status_code < 500:
                logger.warning(
                    f"Client error {response.status_code} for item {item_id}, not retrying."
                )
                break
            else:
                logger.warning(
                    f"Unexpected status code {response.status_code} for item {item_id}"
                )
                retries += 1
        except (httpx.RequestError, httpx.TimeoutException) as e:
            logger.error(f"Error fetching item {item_id}: {e}")
            time.sleep(1)

    logger.error(f"Failed to fetch item {item_id} after {MAX_RETRIES} retries.")
    raise ValueError(f"Failed to fetch item {item_id} after retries.")


def fetch_items(item_ids):
    results = []
    with ThreadPoolExecutor(MAX_WORKERS) as executor:
        future_to_id = {
            executor.submit(fetch_item, item_id): item_id for item_id in item_ids
        }
        for future in as_completed(future_to_id):
            item_id = future_to_id[future]
            try:
                data = future.result()
                results.append((item_id, data))
            except Exception as exc:
                logger.error(f"Item {item_id} generated an exception: {exc}")
    return results


def save_csv(data, columns, filename="results.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        for _, item_data in data:
            row = [item_data.get(col, "") for col in columns]
            writer.writerow(row)


def main():
    item_ids = list(range(1, 1001))
    results = fetch_items(item_ids)

    sorted_results = sorted(results, key=lambda x: x[0])

    for item_id, data in sorted_results:
        logger.info(f"Item ID {item_id}: {data}")

    columns = [
        "order_id",
        "account_id",
        "company",
        "status",
        "currency",
        "subtotal",
        "tax",
        "total",
        "created_at",
    ]

    save_csv(sorted_results, columns)


if __name__ == "__main__":
    main()
