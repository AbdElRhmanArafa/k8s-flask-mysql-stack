from flask import Flask, request, jsonify, render_template
import os
import mysql.connector
import time
import socket
from healthcheck import HealthCheck

app = Flask(__name__)

# Health check setup
health = HealthCheck(app, "/health")

# Database configuration
def get_db_config():
    return {
        'host': os.environ.get('DB_HOST', 'mysql'),
        'user': os.environ.get('DB_USER', 'flaskuser'),
        'password': os.environ.get('DB_PASSWORD', 'flaskpassword'),
        'database': os.environ.get('DB_NAME', 'flaskapp')
    }

# Function to get database connection
def get_db_connection():
    retries = 5
    delay = 5
    for attempt in range(retries):
        try:
            return mysql.connector.connect(**get_db_config())
        except mysql.connector.Error as err:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

# Initialize database tables
def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error initializing database: {err}")

# Health check function for db
def db_available():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True, "Database connection ok"
    except Exception as e:
        return False, str(e)

health.add_check(db_available)

@app.route('/')
def home():
    hostname = socket.gethostname()
    return render_template('index.html', hostname=hostname)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks")
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "tasks": tasks})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    try:
        task_data = request.get_json()
        title = task_data.get('title')
        description = task_data.get('description')
        status = task_data.get('status', 'pending')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
            (title, description, status)
        )
        conn.commit()
        task_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "task_id": task_id}), 201
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        task = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if task:
            return jsonify({"status": "success", "task": task})
        return jsonify({"status": "error", "message": "Task not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        task_data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if 'title' in task_data:
            update_fields.append("title = %s")
            params.append(task_data['title'])
        if 'description' in task_data:
            update_fields.append("description = %s")
            params.append(task_data['description'])
        if 'status' in task_data:
            update_fields.append("status = %s")
            params.append(task_data['status'])
            
        if not update_fields:
            return jsonify({"status": "error", "message": "No fields to update"}), 400
            
        params.append(task_id)
        
        query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, tuple(params))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        
        if affected_rows:
            return jsonify({"status": "success", "message": "Task updated"})
        return jsonify({"status": "error", "message": "Task not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
        affected_rows = cursor.rowcount
        cursor.close()
        conn.close()
        
        if affected_rows:
            return jsonify({"status": "success", "message": "Task deleted"})
        return jsonify({"status": "error", "message": "Task not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/load-test', methods=['POST'])
def load_test():
    """Endpoint to generate test load on the application"""
    try:
        count = request.json.get('count', 10)  # Default to 10 records
        tasks = []
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for i in range(count):
            title = f"Test Task {i}"
            description = f"This is a test task created for load testing ({i})"
            status = "test"
            
            cursor.execute(
                "INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s)",
                (title, description, status)
            )
            tasks.append({"title": title, "description": description, "status": status})
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": f"Created {count} test tasks", "tasks": tasks})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/status')
def status():
    """System status and information endpoint"""
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    return jsonify({
        "status": "operational",
        "timestamp": time.time(),
        "hostname": hostname,
        "ip": ip_address,
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "version": os.environ.get("APP_VERSION", "1.0.0")
    })

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
