import sqlite3

def init_db():
    conn = sqlite3.connect("servers.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS servers (
            user_id INTEGER,
            server_name TEXT,
            ip TEXT,
            username TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_server(user_id, server_name, ip, username, password):
    conn = sqlite3.connect("servers.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO servers (user_id, server_name, ip, username, password)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, server_name, ip, username, password))
    conn.commit()
    conn.close()

def get_servers_by_user(user_id):
    conn = sqlite3.connect("servers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT server_name, ip, username FROM servers WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_full_servers_by_user(user_id):
    conn = sqlite3.connect("servers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT server_name, ip, username, password FROM servers WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_server_by_index(user_id, index):
    conn = sqlite3.connect("servers.db")
    cursor = conn.cursor()
    cursor.execute('SELECT rowid FROM servers WHERE user_id = ?', (user_id,))
    rows = cursor.fetchall()
    if index < 0 or index >= len(rows):
        conn.close()
        return False
    rowid_to_delete = rows[index][0]
    cursor.execute('DELETE FROM servers WHERE rowid = ?', (rowid_to_delete,))
    conn.commit()
    conn.close()
    return True
