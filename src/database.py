import sqlite3
import json

class GameDatabase:
    def __init__(self, db_path="game_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.init_db()
        
    def init_db(self):
        """Crea las tablas necesarias si no existen"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY,
                date TEXT,
                player1_score INTEGER,
                player2_score INTEGER,
                duration INTEGER,
                mine_positions TEXT
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                total_score INTEGER,
                games_played INTEGER,
                best_score INTEGER
            )
        """)
        self.conn.commit()
        
    def save_game_state(self, game_data):
        """Guarda el estado de una partida"""
        self.cursor.execute("""
            INSERT INTO games (date, player1_score, player2_score, 
                             duration, mine_positions)
            VALUES (?, ?, ?, ?, ?)
        """, (game_data["date"], game_data["player1_score"],
              game_data["player2_score"], game_data["duration"],
              json.dumps(game_data["mine_positions"])))
        self.conn.commit()
        
    def update_player_stats(self, player_name, score):
        """Actualiza estadísticas del jugador"""
        self.cursor.execute("""
            INSERT OR REPLACE INTO players (name, total_score, games_played, best_score)
            VALUES (
                ?,
                COALESCE((SELECT total_score FROM players WHERE name = ?) + ?, ?),
                COALESCE((SELECT games_played FROM players WHERE name = ?) + 1, 1),
                MAX(COALESCE((SELECT best_score FROM players WHERE name = ?), 0), ?)
            )
        """, (player_name, player_name, score, score, player_name, player_name, score))
        self.conn.commit()