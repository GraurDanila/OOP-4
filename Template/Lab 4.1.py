import psycopg2
from flask import Flask, request, jsonify ,render_template,redirect ,url_for, session 
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import secrets 

app = Flask(__name__)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('main.html')

@app.route('/home')
def home_page():
    return render_template('home.html')

@app.route('/login_page_render')
def login_page_render():
    return render_template('login.html')

@app.route('/sign_up_page')
def sign_up_page():
    return render_template('sign_up.html')

# Configurația pentru Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'graurdanila5@gmail.com'
app.config['MAIL_PASSWORD'] = 'pqta nvqf haxy mnap'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

# Funcție pentru generarea token-ului de resetare a parolei
def generate_reset_token():
    return secrets.token_urlsafe(32)

# Funcție pentru a obține o conexiune la baza de date
def get_db_connection():
    try:
        connection = psycopg2.connect(connection_string)
        return connection
    except psycopg2.Error as error:
        print("Eroare la conectare la baza de date:", error)
        return None

@app.route('/signup', methods=['POST'])
def signup():
    connection = get_db_connection()
    if connection:
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        session['email'] = email
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", (username, email, password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            return render_template('home.html')
            
        except psycopg2.Error as e:
            print("Eroare la inserarea utilizatorului în baza de date:", e)
            connection.rollback()
            connection.close()
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Failed to connect to database"}), 500
        

app.secret_key = 'your_very_secret_key_here'

@app.route('/login', methods=['POST'])
def login():
    connection = get_db_connection()
    if connection:
        email = request.form['email']
        password = request.form['password']
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                if bcrypt.check_password_hash(user[3], password):
                    session['email'] = email
                    cursor.close()
                    connection.close()
                    return redirect(url_for('home.html'))
                    return jsonify({"message": "Login successful"}), 200
                else:
                    cursor.close()
                    connection.close()
                    return jsonify({"error": "Invalid credentials"}), 401
            else:
                cursor.close()
                connection.close()
                return jsonify({"error": "User not found"}), 404
        except psycopg2.Error as e:
            print("Eroare la interogarea bazei de date pentru login:", e)
            connection.close()
            return jsonify({"error": "Internal server error"}), 500
    else:
        return jsonify({"error": "Failed to connect to database"}), 500

# Connection string cu datele furnizate
connection_string = "postgresql://neondb_owner:yRhiZWNo0pX9@ep-white-thunder-a2u08n9n.eu-central-1.aws.neon.tech/neondb?sslmode=require"

if __name__ == "__main__":
    app.run(debug=True)