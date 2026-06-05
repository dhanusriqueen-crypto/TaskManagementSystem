from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db():
    conn = sqlite3.connect('tasks.db')
    return conn


# ---------------------------
# HOME + FILTERS
# ---------------------------
@app.route('/')
def home():
    filter_type = request.args.get('filter', 'all')

    conn = get_db()
    cur = conn.cursor()

    if filter_type == 'pending':
        cur.execute("SELECT * FROM tasks WHERE done=0")
    elif filter_type == 'completed':
        cur.execute("SELECT * FROM tasks WHERE done=1")
    else:
        cur.execute("SELECT * FROM tasks")

    tasks = cur.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)


# ---------------------------
# ADD TASK
# ---------------------------
@app.route('/add', methods=['POST'])
def add_task():
    task = request.form['task']

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (name, done) VALUES (?, ?)", (task, 0))
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------------------
# COMPLETE TASK
# ---------------------------
@app.route('/complete/<int:id>')
def complete_task(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET done=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------------------
# EDIT TASK (simple version)
# ---------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        new_name = request.form['task']
        cur.execute("UPDATE tasks SET name=? WHERE id=?", (new_name, id))
        conn.commit()
        conn.close()
        return redirect('/')

    cur.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cur.fetchone()
    conn.close()

    return render_template('edit.html', task=task)


# ---------------------------
# DELETE TASK
# ---------------------------
@app.route('/delete/<int:id>')
def delete_task(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')


# ---------------------------
# INIT DATABASE (run once)
# ---------------------------
def init_db():
    conn = sqlite3.connect('tasks.db')
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ---------------------------
# START APP
# ---------------------------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)