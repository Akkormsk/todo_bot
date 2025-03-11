import sqlite3


def init_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        completed INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def add_task(description):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (description) VALUES (?)", (description,))
    conn.commit()
    conn.close()


def get_tasks():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, description, completed FROM tasks WHERE completed = 0")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def toggle_task_completion(task_id):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # Проверяем текущее состояние задачи
    cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
    result = cursor.fetchone()
    if result:
        new_status = 1 if result[0] == 0 else 0  # Переключаем флаг
        cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (new_status, task_id))

        # Если флаг = 1 (задача завершена) — перемещаем в архив и удаляем
        if new_status == 1:
            cursor.execute("INSERT INTO archive (description) SELECT description FROM tasks WHERE id = ?", (task_id,))
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()


def get_archive():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("SELECT description FROM archive")
    archive = cursor.fetchall()
    conn.close()
    return archive


def clear_archive_db():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM archive")
    conn.commit()
    conn.close()