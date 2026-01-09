from flask import Flask , request , jsonify
import psycopg2
from psycopg2 import sql

app = Flask(__name__)

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
def create_tb_if_not_exist():
    connection = get_db_connection()
    cursor = connection.cursor()
  
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS todo_db(
    task_id SERIAL PRIMARY KEY,
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
@app.route("/create_task", methods=['POST'])
def create_task():
    title = request.json['title']
    description = request.json['description']
    duedate = request.json['duedate']
    priority = request.json['priority']
    status = request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO todo_db(title, description, duedate, priority, status)
        VALUES(%s, %s, %s, %s, %s)
    """, (title, description, duedate, priority, status))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"Task created successfully"}),200
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
@app.route('/update_task',methods = ['PUT'])
def update_task():
    task_id = request.json['task_id']
    title = request.json['title']
    description = request.json['description']
    duedate = request.json['duedate']
    priority = request.json['priority']
    status = request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
          UPDATE todo_db
                    SET title = %s,description = %s,duedate = %s,priority = %s,status = %s where task_id = %s;
""",(title,description,duedate,priority,status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"user update successfully"}),201
@app.route('/update_status',methods = ['PUT'])
def update_status():
    task_id = request.json['task_id']
    status = request.json['status']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
          UPDATE todo_db
                    SET status = %s where task_id = %s;
""",(status,task_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"user update successfully"}),201
@app.route('/delete_task', methods=['DELETE'])
def delete_task():
    task_id = request.args.get('task_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       DELETE FROM todo_db WHERE task_id=%s;
    """, (task_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "user deleted successfully"}), 200
if  __name__=='__main__':
   app.run(debug = True)