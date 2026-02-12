from flask import Flask , request , jsonify
import psycopg2
from flask_bcrypt import Bcrypt
import jwt #pip install PyJWT
import datetime

app = Flask(__name__)

bcrypt = Bcrypt(app)


#database configuration
DB_HOST='localhost'
DB_NAME='postgres'
DB_USER='postgres'
DB_PASSWORD='2006'

def get_db_connection():
    connection=psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
    return connection

def create_table_if_not_exists():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_table_if_not_exists()


def create_tb_if_not_exist():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todo_dbs(
    task_id SERIAL PRIMARY KEY,
    user_id INTEGER,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    duedate TEXT NOT NULL,
    priority TEXT DEFAULT 'Medium',
    status TEXT DEFAULT 'Pending'
        );   
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_tb_if_not_exist()

# Secret Key
SECRET_KEY = "this is my secret key this is my secret key!!"

#JWT FUNCTIONS 
def create_jwt(user_id, username):
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def verify_jwt(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data
    except:
        return None


#  SIGNUP API 
@app.route("/signup", methods=["POST"])
def signup():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if not username or not email or not password:
        return jsonify({"error": "All fields required"}), 400

    # Hash Password
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
            INSERT INTO users(username,email,password)
            VALUES(%s,%s,%s)
            RETURNING user_id
        """, (username, email, hashed_password))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    # Create Token
    token = create_jwt(user_id, username)
    return jsonify({
        "message": "Signup successful",
        "token": token
    }), 201

# LOGIN API 
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "All fields required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, username, password
        FROM users
        WHERE email = %s
    """, (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id, username, hashed_password = user

    # Verify Password
    if not bcrypt.check_password_hash(hashed_password, password):
        return jsonify({"error": "Invalid password"}), 401

    # Create Token
    token = create_jwt(user_id, username)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user_id,
            "username": username,
            "email": email
        }
    }), 200

@app.route("/create_task", methods=['POST'])
def create_task():
    token = request.headers.get("Authorization")
    if not token :
        return jsonify({"error":"token invaild"}),401

    user_data = verify_jwt(token)

    if user_data is None:
        return jsonify({"error": "Invalid or expired token"}), 401

    title = request.json['title']
    description = request.json['description']
    duedate = request.json['duedate']
    priority = request.json['priority']
    status = request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO todo_dbs(user_id, title, description, duedate, priority, status)
        VALUES(%s, %s, %s, %s, %s, %s)
    """, (user_data["user_id"], title, description, duedate, priority, status))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"task completed"}),201

@app.route("/get_task",methods = ['GET'])
def get_task():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
             SELECT * FROM todo_db;
    """)
    task_id = cursor.fetchall()
    cursor.close()
    connection.close()
    result =[
            {"task_id":task[0],
            "title":task[1],
            "description":task[2],
            "duedate":task[3],
            "priority":task[4],
            "status":task[5]} for task in task_id
    ]
    return jsonify(result),200

@app.route("/update_apply/<int:task_id>",methods =['PUT'])
def update_apply(task_id):
    token = request.headers.get("Authorization")

    if not token :
        return jsonify({"error":"token invaild"}),401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"error": "Invalid or expired token"}), 401

    title = request.json['title']
    description = request.json['description']
    duedate = request.json['duedate']
    priority = request.json['priority']
    status = request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT * FROM todo_dbs  where task_id =%s AND user_id =%s
""",(task_id,user_data['user_id']))
    cursor.fetchone()
    cursor.execute("""
           UPDATE todo_dbs SET title=%s,description=%s,duedate=%s,priority=%s,status=%s
                   WHERE task_id=%s ;
                   
""",(title, description, duedate, priority, status, task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"task updated successfully"}),201

@app.route("/delete_apply/<int:task_id>",methods =['DELETE'])
def delete_apply(task_id):
    token = request.headers.get("Authorization")

    if not token :
        return jsonify({"error":"token invaild"}),401
    user_data = verify_jwt(token)
    if user_data is None:
        return jsonify({"error": "Invalid or expired token"}), 401

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            SELECT * FROM todo_dbs  where task_id =%s AND user_id =%s
""",(task_id,user_data['user_id']))
    cursor.fetchone()
    cursor.execute("""
           DELETE  FROM todo_dbs WHERE task_id=%s ;
                   
""",(task_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"Form deleted successfully"}),201

if  __name__=='__main__':
   app.run(debug = True)