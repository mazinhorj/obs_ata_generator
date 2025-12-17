import sqlite3

DB_NAME = "atas.db"


def init_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS observacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT,
            texto TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_observacao(tipo, texto):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute('INSERT INTO observacoes (tipo, texto) VALUES (?, ?)', (tipo, texto))
    conn.commit()
    conn.close()


def get_observacoes():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute('SELECT id, tipo, texto FROM observacoes')
    data = c.fetchall()
    conn.close()
    return data


def delete_observacao(obs_id):
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute('DELETE FROM observacoes WHERE id = ?', (obs_id,))
    conn.commit()
    conn.close()


def clear_db():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    c = conn.cursor()
    c.execute('DELETE FROM observacoes')
    conn.commit()
    conn.close()
