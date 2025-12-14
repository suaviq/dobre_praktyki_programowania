import csv
import os
import time
from datetime import datetime
import fcntl
import sys

QUEUE_FILE = "job_queue.csv"
CHECK_INTERVAL = 5
JOB_DURATION = 30
LOCK_TIMEOUT = 10

def acquire_file_lock(file_handle):
    start_time = time.time()
    while True:
        try:
            fcntl.flock(file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except IOError:
            if time.time() - start_time > LOCK_TIMEOUT:
                return False
            time.sleep(0.1)

def release_file_lock(file_handle):
    fcntl.flock(file_handle, fcntl.LOCK_UN)

def read_jobs():
    if not os.path.exists(QUEUE_FILE):
        return []
    
    with open(QUEUE_FILE, 'r', newline='') as f:
        if not acquire_file_lock(f):
            return []
        reader = csv.DictReader(f)
        jobs = list(reader)
        release_file_lock(f)
    
    return jobs

def write_jobs(jobs):
    with open(QUEUE_FILE, 'w', newline='') as f:
        if not acquire_file_lock(f):
            return False
        
        fieldnames = ['job_id', 'description', 'status', 'created_at', 'started_at', 'completed_at', 'consumer_id']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(jobs)
        
        release_file_lock(f)
    
    return True

def find_and_claim_job(consumer_id):
    jobs = read_jobs()
    
    for job in jobs:
        if job['status'] == 'pending':
            job['status'] = 'in_progress'
            job['started_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            job['consumer_id'] = str(consumer_id)
            
            if write_jobs(jobs):
                return job
            else:
                return None
    
    return None

def complete_job(job_id, consumer_id):
    jobs = read_jobs()
    
    for job in jobs:
        if job['job_id'] == job_id and job['consumer_id'] == str(consumer_id):
            job['status'] = 'done'
            job['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            break
    
    write_jobs(jobs)

def execute_job(job, consumer_id):
    job_id = job['job_id']
    description = job['description']
    
    print(f"[Consumer {consumer_id}] Rozpoczynam: Zadanie #{job_id} - {description}")
    print(f"   Przewidywany czas: {JOB_DURATION}s")
    
    for i in range(JOB_DURATION):
        time.sleep(1)
        if (i + 1) % 10 == 0:
            print(f"   [Consumer {consumer_id}] Zadanie #{job_id}: {i + 1}/{JOB_DURATION}s")
    
    complete_job(job_id, consumer_id)
    print(f"[Consumer {consumer_id}] Ukonczono: Zadanie #{job_id}\n")

def get_queue_stats():
    jobs = read_jobs()
    
    pending = sum(1 for job in jobs if job['status'] == 'pending')
    in_progress = sum(1 for job in jobs if job['status'] == 'in_progress')
    done = sum(1 for job in jobs if job['status'] == 'done')
    total = len(jobs)
    
    return {
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'total': total
    }

def run_consumer(consumer_id):
    print("=" * 60)
    print(f"CONSUMER #{consumer_id} - Uruchomiony")
    print("=" * 60)
    print(f"Sprawdzanie kolejki co {CHECK_INTERVAL}s")
    print(f"Czas wykonania zadania: {JOB_DURATION}s")
    print(f"Plik kolejki: {QUEUE_FILE}")
    print("=" * 60)
    print()
    
    iteration = 0
    
    while True:
        iteration += 1
        
        job = find_and_claim_job(consumer_id)
        
        if job:
            execute_job(job, consumer_id)
        else:
            stats = get_queue_stats()
            
            if iteration % 3 == 1:
                print(f"[Consumer {consumer_id}] Brak zadan. Statystyki kolejki:")
                print(f"   Oczekujace: {stats['pending']} | W trakcie: {stats['in_progress']} | Ukonczone: {stats['done']} | Razem: {stats['total']}")
            
            if stats['pending'] == 0 and stats['in_progress'] == 0 and stats['total'] > 0:
                print(f"\n[Consumer {consumer_id}] Wszystkie zadania ukonczone!")
                print(f"   Wykonano {stats['done']} zadan")
                print(f"\n[Consumer {consumer_id}] Zamykam...")
                break
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            consumer_id = int(sys.argv[1])
        except ValueError:
            print("Podaj prawidlowy numer konsumenta")
            print("Uzycie: python consumer.py [numer_konsumenta]")
            sys.exit(1)
    else:
        consumer_id = 1
    
    try:
        run_consumer(consumer_id)
    except KeyboardInterrupt:
        print(f"\n\n[Consumer {consumer_id}] Przerwano przez uzytkownika")
        sys.exit(0)
