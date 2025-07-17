import queue as queue_module
import threading
import time
from os import cpu_count

from .algorithms import algorithms

MAJOR_FORMAT_VERSION = 1


def worker(task_queue, result_queue):
    while True:
        item = task_queue.get()
        if item is None:
            print("[Worker] Received shutdown signal.")
            task_queue.task_done()
            break
        algorithm, action, data = item
        print(f"[Worker] Processing {action} with {algorithm.__name__}")
        if action == 'compress':
            compressed_data = algorithm.compress(data)
            result_queue.put((algorithm, compressed_data))
        elif action == 'decompress':  # Currently has no use as decompression must be done in order
            decompressed_data = algorithm.decompress(data)
            result_queue.put((algorithm, decompressed_data))
        print(f"[Worker] Finished {action} with {algorithm.__name__}")
        task_queue.task_done()


def compress(filename, output, num_threads=None, worker_timeout=None, max_rounds=None):
    if not num_threads:
        num_threads = cpu_count() or 1
    print(f"[Main] Using {num_threads} threads for compression.")
    print(f"[Main] Starting compression for {filename}...")
    with open(filename, 'rb') as file:
        data = file.read()
        original_size = len(data)
        print(f"[Main] Original data size: {original_size} bytes.")
        algorithms_used = []
        round_num = 1
        while True:
            if max_rounds is not None and round_num > max_rounds:
                print(f"[Main] Maximum rounds reached ({max_rounds}). Stopping compression.")
                break
            print(f"[Main] Compression round {round_num}...")
            starting_size = len(data)
            best_size = starting_size
            best_data = data
            best_algorithm = None
            task_queue = queue_module.Queue()
            result_queue = queue_module.Queue()
            threads = []
            for _ in range(num_threads):
                t = threading.Thread(target=worker, args=(task_queue, result_queue))
                t.start()
                threads.append(t)
            for algorithm in algorithms:
                print(f"[Main] Queueing {algorithm.__name__} for compression.")
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
                            print("[Main] Worker timeout reached. Skipping unfinished algorithms.")
                            break
                        algorithm, compressed_data = result_queue.get(timeout=timeout)
                    else:
                        algorithm, compressed_data = result_queue.get()
                except queue_module.Empty:
                    print("[Main] Worker timeout reached. Skipping unfinished algorithms.")
                    break
                if algorithm in finished_algorithms:
                    continue
                finished_algorithms.add(algorithm)
                print(f"[Main] {algorithm.__name__} produced {len(compressed_data)} bytes.")
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
                print(f"[Main] No further compression possible in round {round_num}.")
                break
            data = best_data
            algorithms_used.append(best_algorithm.ID)
            print(f"[Main] Saved {starting_size - best_size} bytes using {best_algorithm.__name__}")
            round_num += 1
        algorithms_used.reverse()
        output_file = output or f"{filename}.cmpo"
        print(f"[Main] Writing compressed data to {output_file}...")
        with open(output_file, 'wb') as out_file:
            out_file.write(MAJOR_FORMAT_VERSION.to_bytes(1, 'big'))
            out_file.write(len(algorithms_used).to_bytes(1, 'big'))
            for algorithm_id in algorithms_used:
                out_file.write(algorithm_id.to_bytes(1, 'big'))
            out_file.write(best_data)
        new_size = len(best_data)
        if not algorithms_used:
            print("[Main] No compression was effective.")
        else:
            print(
                f"[Main] Compressed data saved to {output_file} ({new_size} bytes) using {len(algorithms_used)} algorithms, "
                f"saving a total of {original_size - new_size} bytes ({(1 - new_size / original_size) * 100:.2f}% "
                f"reduction).")
            print("[Main] Compression complete.")


def decompress(filename, output=None):
    print(f"[Main] Starting decompression for {filename}...")
    with open(filename, 'rb') as file:
        data = file.read()
        if not data:
            print("[Main] File is empty.")
            return
        major_version = data[0]
        if major_version != MAJOR_FORMAT_VERSION:
            print(f"[Main] Unsupported file format version: {major_version}. Expected {MAJOR_FORMAT_VERSION}.")
            return
        num_algorithms = data[1]
        algorithms_used = data[2:2 + num_algorithms]
        compressed_data = data[2 + num_algorithms:]
        print(f"[Main] {num_algorithms} algorithms to reverse. Starting decompression...")
        for i, algorithm_id in enumerate(algorithms_used, 1):
            algorithm = next((alg for alg in algorithms if alg.ID == algorithm_id), None)
            if algorithm is None:
                print(f"[Main] Unknown algorithm ID: {algorithm_id}. Skipping.")
                continue
            print(f"[Main] Decompressing with {algorithm.__name__} (step {i}/{num_algorithms})...")
            compressed_data = algorithm.decompress(compressed_data)
            print(f"[Main] Decompressed with {algorithm.__name__}.")
        print(f"[Main] Decompressed data size: {len(compressed_data)} bytes.")
        output_file = output or (filename.replace('.cmpo', '') if filename.endswith('.cmpo') else filename + '.decmpo')
        print(f"[Main] Writing decompressed data to {output_file}...")
        with open(output_file, 'wb') as out_file:
            out_file.write(compressed_data)
        print(f"[Main] Decompressed data saved to {output_file}.")
        print("[Main] Decompression complete.")
