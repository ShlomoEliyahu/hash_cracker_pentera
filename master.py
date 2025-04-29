from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Tuple, Optional
import requests
import time
import json
import os
import logging

logging.basicConfig(filename="master.log", format='%(levelname)s %(asctime)s %(message)s', filemode='w')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

@dataclass(frozen=True)
class Minion:
    ip: str
    port: str

@dataclass(frozen=True)
class Config:
    minions: List[Minion]
    timeout: int
    retries: int


def read_hashes_from_file(filepath: str) -> List[str]:
    with open(filepath, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def divide_ranges(start: int, end: int, parts: int) -> List[Tuple[int, int]]:
    if parts <= 0:
        raise ValueError("parts have to be positive number")

    total_numbers = end - start
    if total_numbers <= 0:
        raise ValueError("The end of the range cant be smaller than the start of the range")

    step = total_numbers // parts
    remainder = total_numbers % parts

    ranges = []
    current_start = start

    for i in range(parts):
        current_end = current_start + step
        if remainder > 0:
            current_end += 1
            remainder -= 1
        ranges.append((current_start, current_end))
        current_start = current_end

    return ranges


def send_task(hash_to_crack: str, minion: Minion, r_start: int, r_end: int, retries: int, timeout: int) -> Optional[str]:
    ip = minion.ip
    port = minion.port
    url = f"http://{ip}:{port}/crack"
    data = {
        "hash": hash_to_crack,
        "range_start": r_start,
        "range_end": r_end
    }
    attempt = 0
    last_exception = None

    while attempt < retries:
        try:
            logger.info(f"ending task to {ip}:{port} | Range: {r_start}-{r_end}")
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            last_exception = e
            attempt += 1
            logger.error(f"Could not contact minion {ip}:{port} (attempt {attempt}): {e}")

        else:
            result = response.json()
            if result.get("found") is True:
                return result["phone"]
            return None

    if attempt >= retries and last_exception:
        raise last_exception




def crack_single_hash(hash_to_crack: str, config: Config, ranges: List[Tuple[int, int]]) -> Optional[str]:
    with ThreadPoolExecutor(max_workers=min(len(config.minions), 30)) as executor:
        futures = []

        for i, (r_start, r_end) in enumerate(ranges):
            minion = config.minions[i]
            future = executor.submit(send_task, hash_to_crack=hash_to_crack, minion=minion, r_start=r_start, r_end=r_end, retries=config.retries, timeout=config.timeout)
            futures.append(future)

        for future in as_completed(futures):
            try:
                result = future.result()

            except Exception as e:
                logger.error(f"Something went wrong while running send_task function {e}")

            else:
                if result is not None:
                    for f in futures:
                        f.cancel()
                    return result

    return None


def main():
    with open(os.environ.get('config_path')) as f:
        configuration = json.load(f)

    hashes_path = input("Please insert the path of hashes.txt file:\n")
    hashes = read_hashes_from_file(hashes_path)

    if len(hashes) == 0:
        logger.info("Got no hashes")
        exit(1)

    minions = configuration["hosts"]
    timeout = configuration.get("timeout", 180)
    retries = configuration.get("retries", 3)
    range_start = configuration["range_start"]
    range_end = configuration["range_end"]
    ranges = divide_ranges(range_start, range_end, len(minions))

    config = Config(minions=[Minion(ip=minion["ip"], port=minion["port"]) for minion in minions], timeout=timeout, retries=retries)

    for h in hashes:
        logger.info(f"Cracking hash: {h}")
        start_time = time.time()
        try:
            phone = crack_single_hash(h, config, ranges)

        except Exception as ex:
            logger.error(f"Something went wrong inside crack_single_hash function {ex}")
            continue

        if phone:
            logger.info(f"[SUCCESS] Hash {h} => {phone}")

        else:
            logger.info(f"[FAILED] Could not crack hash {h}")

        logger.info(f"[TIME] Elapsed: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()