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
    CREATE TABLE IF NOT EXISTS students_db(
    student_id SERIAL PRIMARY KEY,
    studentname TEXT NOT NULL,
    email TEXT NOT NULL,
    phonenumber TEXT NOT NULL,
    rollnumber TEXT NOT NULL,
    course TEXT NOT NULL,
    coursecode TEXT NOT NULL
        );   
    """)
    connection.commit()
    cursor.close()
    connection.close()
create_tb_if_not_exist()
@app.route("/student_register", methods=['POST'])
def student_register():
    studentname = request.json['studentname']
    email = request.json['email']
    phonenumber = request.json['phonenumber']
    rollnumber = request.json['rollnumber']
    course = request.json['course']
    coursecode = request.json['coursecode']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO students_db(studentname, email, phonenumber, rollnumber, course, coursecode)
        VALUES(%s, %s, %s, %s, %s, %s)
    """, (studentname, email, phonenumber, rollnumber, course, coursecode))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"Student registered successfully"}),200
@app.route("/get_student",methods = ['GET'])
def get_student():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
             SELECT * FROM students_db;
    """)
    students_db = cursor.fetchall()
    cursor.close()
    connection.close()
    result =[
            {"student_id":student[0],
            "studentname":student[1],
            "email":student[2],
            "phonenumber":student[3],
            "rollnumber":student[4],
            "course":student[5],
            "coursecode":student[6]} for student in students_db
    ]
    return jsonify(result),200
@app.route('/update_student',methods = ['PUT'])
def update_student():
    student_id = request.args['student_id']
    studentname = request.json['studentname']
    email = request.json['email']
    phonenumber = request.json['phonenumber']
    rollnumber = request.json['rollnumber']
    course = request.json['course']
    coursecode = request.json['coursecode']
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
          UPDATE students_db
                    SET studentname = %s,email = %s,phonenumber = %s,rollnumber = %s,course = %s,coursecode = %s where student_id = %s;
""",(studentname,email,phonenumber,rollnumber,course,coursecode,student_id))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message":"student updated successfully"}),201
@app.route('/delete_student', methods=['DELETE'])
def delete_student():
    student_id = request.args.get('student_id')
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
       DELETE FROM students_db WHERE student_id=%s;
    """, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({"message": "student deleted successfully"}), 200
if  __name__=='__main__':
   app.run(debug = True)