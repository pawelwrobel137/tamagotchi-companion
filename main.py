from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3
from datetime import datetime

# Inicjalizacja frameworka serwera webowego (Week 3)
app = FastAPI(title="Virtual Pet Companion API")
DB_NAME = "tamagotchi.db"

# --- WEEK 3: Połączenie z bazą danych i definicja schematu (health, hunger, mood + event logs) ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Schemat tabeli ze statystykami zwierzaka (health, hunger, mood)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pet_stats (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            health INTEGER NOT NULL,
            hunger INTEGER NOT NULL,
            mood INTEGER NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)
    
    # Schemat tabeli z historią zdarzeń (event logs)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS event_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    # Stworzenie zwierzaka ze startowymi statystykami, jeśli baza jest pusta
    cursor.execute("SELECT COUNT(*) FROM pet_stats")
    if cursor.fetchone()[0] == 0:
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO pet_stats (id, name, health, hunger, mood, last_updated)
            VALUES (1, 'TamaBot', 100, 20, 90, ?)
        """, (now,))
        cursor.execute("""
            INSERT INTO event_logs (event_type, description, timestamp)
            VALUES ('SYSTEM_INIT', 'Initialized virtual pet with default stats.', ?)
        """, (now,))
        
    conn.commit()
    conn.close()

# Uruchomienie bazy przy starcie serwera
init_db()

# Struktura zapytania JSON do aktualizacji stanu zwierzaka
class PetUpdateRequest(BaseModel):
    health: Optional[int] = None
    hunger: Optional[int] = None
    mood: Optional[int] = None
    action: Optional[str] = "REMOTE_CARE_COMMAND"

# --- WEEK 4: Endpointy REST API do odczytu i aktualizacji stanu ---

@app.get("/api/pet")
def get_pet_state():
    """Endpoint GET do odczytu aktualnych statystyk zwierzaka."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pet_stats WHERE id = 1")
    pet = cursor.fetchone()
    conn.close()
    
    if not pet:
        raise HTTPException(status_code=404, detail="Pet not found")
    return dict(pet)

@app.post("/api/pet/update")
def update_pet_state(update: PetUpdateRequest):
    """Endpoint POST do aktualizacji statystyk zwierzaka i zapisu w event logs."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM pet_stats WHERE id = 1")
    current = cursor.fetchone()
    
    new_health = update.health if update.health is not None else current["health"]
    new_hunger = update.hunger if update.hunger is not None else current["hunger"]
    new_mood = update.mood if update.mood is not None else current["mood"]
    now = datetime.now().isoformat()
    
    cursor.execute("""
        UPDATE pet_stats
        SET health = ?, hunger = ?, mood = ?, last_updated = ?
        WHERE id = 1
    """, (new_health, new_hunger, new_mood, now))
    
    log_desc = f"Stats updated -> health: {new_health}, hunger: {new_hunger}, mood: {new_mood}"
    cursor.execute("""
        INSERT INTO event_logs (event_type, description, timestamp)
        VALUES (?, ?, ?)
    """, (update.action, log_desc, now))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "message": "Virtual pet state updated",
        "pet_stats": {
            "health": new_health,
            "hunger": new_hunger,
            "mood": new_mood,
            "last_updated": now
        }
    }

@app.get("/api/logs")
def get_event_logs():
    """Endpoint GET do przeglądania logów historycznych (event logs)."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM event_logs ORDER BY id DESC")
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"event_logs": logs}