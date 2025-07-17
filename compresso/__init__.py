import queue as queue_module
import threading
import time
from os import cpu_count
import logging

from .algorithms import algorithms

MAJOR_FORMAT_VERSION = 1


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='[%(levelname)s] %(message)s',
        force=True
    )


def worker(task_queue, result_queue, verbose=False):
    while True:
        item = task_queue.get()
        if item is None:
            logging.debug("[Worker] Received shutdown signal.")
            task_queue.task_done()
            break
        algorithm, action, data = item
        logging.debug(f"[Worker] Processing {action} with {algorithm.__name__}")
        if action == 'compress':
            compressed_data = algorithm.compress(data)
            result_queue.put((algorithm, compressed_data))
        elif action == 'decompress':
            decompressed_data = algorithm.decompress(data)
            result_queue.put((algorithm, decompressed_data))
        logging.debug(f"[Worker] Finished {action} with {algorithm.__name__}")
        task_queue.task_done()


def compress(filename, output, num_threads=None, worker_timeout=None, max_rounds=None, verbose=False):
    setup_logging(verbose)
    if not num_threads:
        num_threads = cpu_count() or 1
    logging.info(f"[Main] Using {num_threads} threads for compression.")
    logging.info(f"[Main] Starting compression for {filename}...")
    with open(filename, 'rb') as file:
        data = file.read()
        original_size = len(data)
        logging.info(f"[Main] Original data size: {original_size} bytes.")
        algorithms_used = []
        round_num = 1
        while True:
            if max_rounds is not None and round_num > max_rounds:
                logging.info(f"[Main] Maximum rounds reached ({max_rounds}). Stopping compression.")
                break
            logging.debug(f"[Main] Compression round {round_num}...")
            starting_size = len(data)
            best_size = starting_size
            best_data = data
            best_algorithm = None
            task_queue = queue_module.Queue()
            result_queue = queue_module.Queue()
            threads = []
            for _ in range(num_threads):
                t = threading.Thread(target=worker, args=(task_queue, result_queue, verbose))
                t.start()
                threads.append(t)
            for algorithm in algorithms:
                logging.debug(f"[Main] Queueing {algorithm.__name__} for compression.")
                task_queue.put((algorithm, 'compress', data))
            for _ in threads:
                task_queue.put(None)
            num_results = 0
            total_tasks = len(algorithms)
            finished_algorithms = set()
            start_time = time.time()
            while num_results < total_tasks:
                try:
                    if worker_timeout is not None:
                        timeout = max(0, worker_timeout - (time.time() - start_time))
                        if timeout == 0:
                            logging.info("[Main] Worker timeout reached. Skipping unfinished algorithms.")
                            break
                        algorithm, compressed_data = result_queue.get(timeout=timeout)
                    else:
                        algorithm, compressed_data = result_queue.get()
                except queue_module.Empty:
                    logging.info("[Main] Worker timeout reached. Skipping unfinished algorithms.")
                    break
                if algorithm in finished_algorithms:
                    continue
                finished_algorithms.add(algorithm)
                logging.debug(f"[Main] {algorithm.__name__} produced {len(compressed_data)} bytes.")
                if len(compressed_data) < best_size:
                    best_size = len(compressed_data)
                    best_data = compressed_data
                    best_algorithm = algorithm
                num_results += 1
                del compressed_data  # Free memory immediately
            # --- FORCE STOP ALL WORKERS IMMEDIATELY ---
            while not task_queue.empty():
                try:
                    task_queue.get_nowait()
                    task_queue.task_done()
                except Exception:
                    break
            for _ in threads:
                task_queue.put(None)
            for t in threads:
                t.join(timeout=1)
            # --- END FORCE STOP ---
            if best_algorithm is None or best_size >= starting_size:
                logging.info(f"[Main] No further compression possible in round {round_num}.")
                break
            data = best_data
            algorithms_used.append(best_algorithm.ID)
            logging.info(f"[Main] Saved {starting_size - best_size} bytes using {best_algorithm.__name__}")
            round_num += 1
        algorithms_used.reverse()
        output_file = output or f"{filename}.cmpo"
        logging.info(f"[Main] Writing compressed data to {output_file}...")
        with open(output_file, 'wb') as out_file:
            out_file.write(MAJOR_FORMAT_VERSION.to_bytes(1, 'big'))
            out_file.write(len(algorithms_used).to_bytes(1, 'big'))
            for algorithm_id in algorithms_used:
                out_file.write(algorithm_id.to_bytes(1, 'big'))
            out_file.write(best_data)
        new_size = len(best_data)
        if not algorithms_used:
            logging.info("[Main] No compression was effective.")
        else:
            logging.info(
                f"[Main] Compressed data saved to {output_file} ({new_size} bytes) using {len(algorithms_used)} algorithms, "
                f"saving a total of {original_size - new_size} bytes ({(1 - new_size / original_size) * 100:.2f}% "
                f"reduction).")
            logging.info("[Main] Compression complete.")


def decompress(filename, output=None, verbose=False):
    setup_logging(verbose)
    logging.info(f"[Main] Starting decompression for {filename}...")
    with open(filename, 'rb') as file:
        data = file.read()
        if not data:
            logging.info("[Main] File is empty.")
            return
        major_version = data[0]
        if major_version != MAJOR_FORMAT_VERSION:
            logging.info(f"[Main] Unsupported file format version: {major_version}. Expected {MAJOR_FORMAT_VERSION}.")
            return
        num_algorithms = data[1]
        algorithms_used = data[2:2 + num_algorithms]
        compressed_data = data[2 + num_algorithms:]
        logging.info(f"[Main] {num_algorithms} algorithms to reverse. Starting decompression...")
        for i, algorithm_id in enumerate(algorithms_used, 1):
            algorithm = next((alg for alg in algorithms if alg.ID == algorithm_id), None)
            if algorithm is None:
                logging.info(f"[Main] Unknown algorithm ID: {algorithm_id}. Skipping.")
                continue
            logging.debug(f"[Main] Decompressing with {algorithm.__name__} (step {i}/{num_algorithms})...")
            compressed_data = algorithm.decompress(compressed_data)
            logging.debug(f"[Main] Decompressed with {algorithm.__name__}.")
        output_file = output or filename.rsplit('.', 1)[0]
        with open(output_file, 'wb') as out_file:
            out_file.write(compressed_data)
        logging.info(f"[Main] Decompression complete. Output written to {output_file}.")
