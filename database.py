import sqlite3


def add_player(user_id, name):
    progress = "yard"
    db = sqlite3.connect("players.db")
    cur = db.cursor()
    check_prog = cur.execute(f"SELECT progress, events FROM players WHERE user_id={user_id}").fetchall()
    if not check_prog:
        with db:
            cur.execute(f"INSERT INTO players (user_id, name, progress, events) VALUES ({user_id}, '{name}', "
                        f"'{progress}', '')")
        db.close()
        return ["yard", '']
    else:
        db.close()
        return [check_prog[0][0], check_prog[0][1]]


def update_user(user_id, p, event):
    db = sqlite3.connect("players.db")
    cur = db.cursor()
    with db:
        cur.execute(f"UPDATE players SET progress='{p}', events='{event}' WHERE user_id={user_id}").fetchall()
    db.close()
