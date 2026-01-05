import sqlite3
import time
from datetime import datetime
import sys

DB_FILE = "job_queue.db"

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
    print(f"Baza danych gotowa: {DB_FILE}")

def add_job(description):
    """Dodaje nowe zadanie do kolejki w bazie danych"""
    initialize_database()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO jobs (description, status, created_at)
        VALUES (?, 'pending', ?)
    ''', (description, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
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
    print("PRODUCER - System Kolejki Zadan (SQLite)")  # Dodano informację o SQLite
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
