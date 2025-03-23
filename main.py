from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime

app = Flask(__name__)

db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "api_flask"
}

def db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def root():
    return 'Home de Jean'

@app.route('/users', methods=['GET'])
def get_user():
    try:
        conn = db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario")
        usuarios = cursor.fetchall()

        for usuario in usuarios:
            usuario['fecha_creacion'] = usuario['fecha_creacion'].strftime("%Y-%m-%d %H:%M:%S")

        cursor.close()
        conn.close()

        return jsonify(usuarios), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if not nombre or not email:
        return jsonify({"error": "Nombre y email son obligatorios"}), 400
    
    conn = db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuario(nombre, email, fecha_creacion) VALUES (%s, %s, %s)", (nombre, email, fecha_creacion))
        conn.commit()
        status = "usuario creado"
    except mysql.connector.Error as err:
        status = f"Error: {err}"
    finally:
        cursor.close()
        conn.close()
    
    return jsonify({"nombre": nombre, "email": email, "status": status}), 200

@app.route('/update-user', methods=['POST'])
def update_user():
    data = request.get_json()
    user_id = data.get("id")
    nombre = data.get("nombre")
    email = data.get("email")
    fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        if not user_id:
            return jsonify({"error": "ID del usuario es requerido"}), 400
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE usuario SET nombre = %s, email = %s, fecha_creacion = %s WHERE id = %s", (nombre, email, fecha_creacion, user_id))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Usuario Actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete-user', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = data.get("id")
    try:
        if not user_id:
            return jsonify({"error": "ID del usuario es requerido"}), 400
        
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuario WHERE id = %s", (user_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Usuario eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)