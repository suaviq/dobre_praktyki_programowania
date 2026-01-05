import sqlite3
import time
from datetime import datetime
import sys

DB_FILE = "job_queue.db"
CHECK_INTERVAL = 5
JOB_DURATION = 30

def initialize_database():
    """Tworzy bazę danych i tabelę jeśli nie istnieją"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            started_at TEXT,
            completed_at TEXT,
            consumer_id INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

def read_jobs():
    """Odczytuje wszystkie zadania z bazy danych"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM jobs')
    jobs = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return jobs

def find_and_claim_job(consumer_id):
    """Znajduje i przypisuje zadanie do konsumenta (atomowa operacja)"""
    conn = sqlite3.connect(DB_FILE)
    conn.isolation_level = 'EXCLUSIVE'  # Blokada całej bazy dla atomowości
    cursor = conn.cursor()
    
    try:
        conn.execute('BEGIN EXCLUSIVE')
        
        # Znajdź pierwsze zadanie oczekujące
        cursor.execute('''
            SELECT * FROM jobs 
            WHERE status = 'pending' 
            ORDER BY job_id 
            LIMIT 1
        ''')
        
        row = cursor.fetchone()
        
        if row:
            job_id = row[0]
            
            # Aktualizuj status zadania
            cursor.execute('''
                UPDATE jobs 
                SET status = 'in_progress',
                    started_at = ?,
                    consumer_id = ?
                WHERE job_id = ?
            ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), consumer_id, job_id))
            
            conn.commit()
            
            # Pobierz zaktualizowane zadanie
            cursor.execute('SELECT * FROM jobs WHERE job_id = ?', (job_id,))
            updated_row = cursor.fetchone()
            
            job = {
                'job_id': updated_row[0],
                'description': updated_row[1],
                'status': updated_row[2],
                'created_at': updated_row[3],
                'started_at': updated_row[4],
                'completed_at': updated_row[5],
                'consumer_id': updated_row[6]
            }
            
            return job
        else:
            conn.commit()
            return None
            
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Błąd bazy danych: {e}")
        return None
    finally:
        conn.close()

def complete_job(job_id, consumer_id):
    """Oznacza zadanie jako ukończone"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE jobs 
        SET status = 'done',
            completed_at = ?
        WHERE job_id = ? AND consumer_id = ?
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), job_id, consumer_id))
    
    conn.commit()
    conn.close()

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
    """Pobiera statystyki kolejki z bazy danych"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "pending"')
    pending = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "in_progress"')
    in_progress = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jobs WHERE status = "done"')
    done = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM jobs')
    total = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'total': total
    }

def run_consumer(consumer_id):
    initialize_database()
    
    print("=" * 60)
    print(f"CONSUMER #{consumer_id} - Uruchomiony")
    print("=" * 60)
    print(f"Sprawdzanie kolejki co {CHECK_INTERVAL}s")
    print(f"Czas wykonania zadania: {JOB_DURATION}s")
    print(f"Baza danych: {DB_FILE}")  # Zmieniono komunikat
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
