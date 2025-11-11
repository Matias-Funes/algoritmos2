import sqlite3
import json
import datetime

class GameDatabase:
    def __init__(self, db_path="game_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.init_db()
        
    def init_db(self):
        """
        Crea las tablas necesarias si no existen.
        'saved_games' guarda el estado de una simulación interrumpida.
        'statistics' guarda los resultados finales de partidas completadas.
        """
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS saved_games (
                id INTEGER PRIMARY KEY,
                save_name TEXT UNIQUE NOT NULL,
                saved_at TEXT,
                game_state TEXT 
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY,
                date TEXT,
                winner TEXT,
                player1_score INTEGER,
                player2_score INTEGER
            )
        """)
        self.conn.commit()
        
    def save_game_state(self, save_name, game_state_data):
        """
        Guarda o sobrescribe el estado completo de una partida en un 'slot' con nombre.
        'game_state_data' es un gran diccionario de Python.
        """
        try:
            # Convertimos el diccionario de Python a un string JSON
            game_state_json = json.dumps(game_state_data)
            
            # Usamos INSERT OR REPLACE para crear o actualizar el guardado
            self.cursor.execute("""
                INSERT OR REPLACE INTO saved_games (save_name, saved_at, game_state)
                VALUES (?, ?, ?)
            """, (save_name, datetime.datetime.now().isoformat(), game_state_json))
            
            self.conn.commit()
            print(f"Partida '{save_name}' guardada exitosamente.")
        except Exception as e:
            print(f"Error al guardar la partida: {e}")

    def load_game_state(self, save_name):
        """
        Carga el estado de una partida desde la base de datos.
        Devuelve un diccionario de Python.
        """
        self.cursor.execute("SELECT game_state FROM saved_games WHERE save_name = ?", (save_name,))
        result = self.cursor.fetchone()
        
        if result:
            # Convertimos el string JSON de vuelta a un diccionario de Python
            game_state_data = json.loads(result[0])
            print(f"Partida '{save_name}' cargada exitosamente.")
            return game_state_data
        else:
            print(f"No se encontró la partida guardada '{save_name}'.")
            return None
        
    def save_match_result(self, winner_name, p1_score, p2_score):
        """
        Guarda el resultado final de una partida en la tabla 'statistics'.
        """
        try:
            self.cursor.execute("""
                INSERT INTO statistics (date, winner, player1_score, player2_score)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),
                winner_name,
                p1_score,
                p2_score
            ))
            self.conn.commit()
            print("Resultado de la partida guardado en estadísticas.")
        except Exception as e:
            print(f"Error al guardar estadísticas: {e}")

    def get_statistics(self):
        """
        Obtiene todos los resultados de las partidas, ordenados por fecha.
        """
        self.cursor.execute("SELECT date, winner, player1_score, player2_score FROM statistics ORDER BY date DESC")
        return self.cursor.fetchall() # Devuelve una lista de tuplas
