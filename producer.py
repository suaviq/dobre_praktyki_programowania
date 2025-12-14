import csv
import os
import time
from datetime import datetime
import fcntl
import sys

QUEUE_FILE = "job_queue.csv"
LOCK_TIMEOUT = 10

def acquire_file_lock(file_handle):
    start_time = time.time()
    while True:
        try:
            fcntl.flock(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            if time.time() - start_time > LOCK_TIMEOUT:
                print("Timeout podczas blokowania pliku")
                return False
            time.sleep(0.1)

def release_file_lock(file_handle):
    fcntl.flock(file_handle, fcntl.LOCK_UN)

def initialize_queue_file():
    if not os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'w', newline='') as f:
            acquire_file_lock(f)
            writer = csv.writer(f)
            writer.writerow(['job_id', 'description', 'status', 'created_at', 'started_at', 'completed_at', 'consumer_id'])
            release_file_lock(f)
        print(f"Utworzono plik kolejki: {QUEUE_FILE}")

def add_job(description):
    initialize_queue_file()
    
    with open(QUEUE_FILE, 'r', newline='') as f:
        acquire_file_lock(f)
        reader = csv.DictReader(f)
        jobs = list(reader)
        release_file_lock(f)
    
    if jobs:
        last_id = max(int(job['job_id']) for job in jobs)
        new_id = last_id + 1
    else:
        new_id = 1
    
    with open(QUEUE_FILE, 'a', newline='') as f:
        acquire_file_lock(f)
        writer = csv.writer(f)
        writer.writerow([
            new_id,
            description,
            'pending',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '',
            '',
            ''
        ])
        release_file_lock(f)
    
    print(f"Dodano zadanie #{new_id}: {description}")
    return new_id

def add_multiple_jobs(count, description_template="Rozmowa telefoniczna"):
    print(f"\nDodawanie {count} zadan do kolejki...\n")
    
    for i in range(1, count + 1):
        description = f"{description_template} #{i}"
        add_job(description)
        
        if i % 10 == 0:
            print(f"   ({i}/{count} zadan dodanych)")
    
    print(f"\nDodano wszystkie {count} zadan do kolejki!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("PRODUCER - System Kolejki Zadan")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
            add_multiple_jobs(count)
        except ValueError:
            print("Podaj prawidlowa liczbe zadan")
            print("Uzycie: python producer.py [liczba_zadan]")
    else:
        add_multiple_jobs(100)
