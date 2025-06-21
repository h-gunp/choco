from flask import Flask, redirect, request, render_template
import pymysql

app = Flask(__name__)

db_config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root', 
    'password': '?h10720!',
    'db': 'board',
    'charset': 'utf8mb4'
}

def init_db():
    conn = None
    try:
        server_conn_info = db_config.copy()
        del server_conn_info['db']
        conn = pymysql.connect(**server_conn_info)
        
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['db']}")
            conn.select_db(db_config['db'])

        with conn.cursor() as cursor:
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS topic (
                id INT PRIMARY KEY AUTO_INCREMENT,
                title VARCHAR(255) NOT NULL,
                body TEXT NOT NULL
            )
            """
            cursor.execute(create_table_sql)

        print("데이터베이스와 테이블이 성공적으로 준비되었습니다.")

    except Exception as e:
        print(f"데이터베이스 초기화 중 오류 발생: {e}")
    finally:
        if conn:
            conn.close()

def get_db_connection():
    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        db=db_config['db'],
        charset=db_config['charset'],
        cursorclass=pymysql.cursors.DictCursor 
    )
    return conn

@app.route('/')
def main():
    topics_from_db = []
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM topic ORDER BY id DESC"
            cursor.execute(sql)
            topics_from_db = cursor.fetchall()
    except Exception as e:
        print(f"데이터베이스 조회 오류: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('base.html', topics=topics_from_db)

@app.route('/read/<int:id>/')
def read(id):
    conn = None
    try:
        conn = get_db_connection()
        
        with conn.cursor() as cursor:
            sql = "SELECT * FROM topic ORDER BY id DESC"
            cursor.execute(sql)
            all_topics = cursor.fetchall()

        with conn.cursor() as cursor:
            sql = "SELECT * FROM topic WHERE id = %s"
            cursor.execute(sql, (id,))
            topic = cursor.fetchone() 

        if topic is None:
            return "존재하지 않는 게시글입니다. <a href='/'>돌아가기</a>"

        return render_template('read.html', topics=all_topics, topic=topic)

    except Exception as e:
        print(f"데이터베이스 조회 오류: {e}")
        return "오류가 발생했습니다. <a href='/'>돌아가기</a>"
    finally:
        if conn:
            conn.close()

@app.route('/create/', methods=['GET', 'POST'])
def create():
    conn = None
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']
            
            with conn.cursor() as cursor:
                sql = "INSERT INTO topic (title, body) VALUES (%s, %s)"
                cursor.execute(sql, (title, body))
            
            conn.commit()
            
            new_id = cursor.lastrowid
            return redirect(f'/read/{new_id}/')

        else: # request.method == 'GET'
            with conn.cursor() as cursor:
                sql = "SELECT * FROM topic ORDER BY id DESC"
                cursor.execute(sql)
                all_topics = cursor.fetchall()
            return render_template('create.html', topics=all_topics)

    except Exception as e:
        print(f"데이터 처리 오류: {e}")
        return "오류가 발생했습니다. <a href='/'>돌아가기</a>"
    finally:
        if conn:
            conn.close() 

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    conn = None
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']

            with conn.cursor() as cursor:
                sql = "UPDATE topic SET title=%s, body=%s WHERE id=%s"
                cursor.execute(sql, (title, body, id))
            conn.commit()
            return redirect(f'/read/{id}/')

        else:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM topic ORDER BY id DESC"
                cursor.execute(sql)
                all_topics = cursor.fetchall()

            with conn.cursor() as cursor:
                sql = "SELECT * FROM topic WHERE id = %s"
                cursor.execute(sql, (id,))
                topic = cursor.fetchone()

            if topic is None:
                return "존재하지 않는 게시글입니다. <a href='/'>돌아가기</a>"

            return render_template('update.html', topics=all_topics, topic=topic)
            
    except Exception as e:
        print(f"데이터 처리 오류: {e}")
        return "오류가 발생했습니다. <a href='/'>돌아가기</a>"
    finally:
        if conn:
            conn.close()
   
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "DELETE FROM topic WHERE id = %s"
            cursor.execute(sql, (id,))
        conn.commit()
        return redirect('/')
    
    except Exception as e:
        print(f"데이터 처리 오류: {e}")
        return "오류가 발생했습니다. <a href='/'>돌아가기</a>"
    
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)