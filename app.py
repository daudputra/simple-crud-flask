from flask import Flask, render_template, request, redirect, url_for
import MySQLdb
import base64

try:
    db = MySQLdb.connect(host='localhost', user='root', password='', database='crud_flask') #? koneki database
except MySQLdb.Error as e:
    print("Error: ", e)
    print("Error connecting to database")
except Exception as e:
    print("Error: ", e)
    


app = Flask(__name__, template_folder='app/templates')
app.secret_key = '53335'

@app.route('/')
def index():
    db.query('SELECT * FROM user_data')
    result = db.store_result()
    data_raw = result.fetch_row(maxrows=0)

    # ? encode data dari database
    data = []
    for row in data_raw:
        id, name, email, passwords, age, gender, phone_number, image = row # ? agar data bisa di panggil ke html melalui row
        encoded_data = {}
        for key, value in zip(['id', 'name', 'email', 'passwords', 'age', 'gender', 'phone_number', 'image'], row):
            if key == 'image' and isinstance(value, bytes):
                encoded_data[key] = base64.b64encode(value).decode('utf-8')
            else:
                encoded_data[key] = value.decode('utf-8') if isinstance(value, bytes) else value
        data.append(encoded_data)
    return render_template("index.html", data=data)
    
@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']   
        email = request.form['email']
        passwords = request.form['passwords']
        phone_number = request.form['phone_number']
        image = request.files['image'].read() if 'image' in request.files else None
        cursor = db.cursor()
        cursor.execute('INSERT INTO user_data (name, age, email, gender, passwords, phone_number, image) VALUES (%s,%s,%s,%s,%s,%s, %s)', (name, age, email, gender, passwords, phone_number, image))
        db.commit()
        cursor.close()

        return redirect(url_for('index'))
    return render_template('create.html')



@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM user_data WHERE id = %s", (id,))
    db.commit()
    cursor.close()

    return redirect(url_for('index'))





@app.route('/user-detail/<int:id>',methods=(['GET']))
def user_detail(id):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM user_data WHERE id = %s", (id,))
        user = cursor.fetchone()
        if user:
            id, name, email, passwords, age, gender, phone_number, image = user
            encoded_image = base64.b64encode(image).decode('utf-8') if image else None
            user_data = {
                'id': id,
                'name': name,
                'email': email,
                'passwords': passwords,
                'age': age,
                'gender': gender,
                'phone_number': phone_number,
                'image': encoded_image
            }
        else:
            user_data = None
        return render_template('detail_user.html', data_user=user_data)
    except Exception as e:
        print(e)




@app.route('/edit/<int:id>', methods=['POST', 'GET'])
def edit(id):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user_data WHERE id = %s", (id,))
    user = cursor.fetchone()
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        email = request.form['email']
        passwords = request.form['passwords']
        phone_number = request.form['phone_number']
        image = request.files['image'].read() if 'image' in request.files else None

        if image:
            cursor.execute('UPDATE user_data SET name=%s, age=%s, email=%s, gender=%s, passwords=%s, phone_number=%s, image=%s WHERE id=%s',
                            (name, age, email, gender, passwords, phone_number, image, id))
        else:
            cursor.execute('UPDATE user_data SET name=%s, age=%s, email=%s, gender=%s, passwords=%s, phone_number=%s WHERE id=%s',
                            (name, age, email, gender, passwords, phone_number, id))

        db.commit()
        cursor.close()
        return redirect(url_for('index'))

    cursor.close()
    if user:
        id, name, email, passwords, age, gender, phone_number, image = user
        encoded_image = base64.b64encode(image).decode('utf-8') if image else None
        user_data = {
            'id': id,
            'name': name,
            'email': email,
            'passwords': passwords,
            'age': age,
            'gender': gender,
            'phone_number': phone_number,
            'image': encoded_image
        }
    else:
        user_data = None
    return render_template('edit.html', user=user_data)

@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template('404.html')

if __name__ == '__main__':
    app.run(debug=True)