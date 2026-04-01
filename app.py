from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret"

# DB Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harish@1122",
    database="school"
)
cursor = db.cursor(dictionary=True)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('home.html')


# ---------------- ADMIN LOGIN ----------------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        query = "SELECT * FROM admin WHERE Username=%s AND Password=%s"
        cursor.execute(query, (username, password))
        admin = cursor.fetchone()

        if admin:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid Admin Login"

    return render_template('admin_login.html')


# ---------------- STUDENT LOGIN ----------------
@app.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        student_id = request.form['student_id']
        dob = request.form['dob']

        query = "SELECT * FROM student WHERE Student_ID=%s AND DOB=%s"
        cursor.execute(query, (student_id, dob))
        student = cursor.fetchone()

        if student:
            session['student_id'] = student_id
            return redirect(url_for('student_dashboard'))
        else:
            return "Invalid Student Login"

    return render_template('student_login.html')


# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Fetch all data
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM payment")
    payments = cursor.fetchall()

    cursor.execute("SELECT * FROM fee_structure")
    fees = cursor.fetchall()

    cursor.execute("SELECT * FROM receipt")
    receipts = cursor.fetchall()

    return render_template('admin_dashboard.html',
                           students=students,
                           payments=payments,
                           fees=fees,
                           receipts=receipts)


# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student_dashboard')
def student_dashboard():
    if 'student_id' not in session:
        return redirect(url_for('student_login'))

    student_id = session['student_id']

    # Student info
    cursor.execute("SELECT * FROM student WHERE Student_ID=%s", (student_id,))
    student = cursor.fetchone()

    # Payment info
    cursor.execute("SELECT * FROM payment WHERE Student_ID=%s", (student_id,))
    payments = cursor.fetchall()

    # Join with fee_structure
    cursor.execute("""
        SELECT f.Class, f.Amount, f.Due_Date
        FROM fee_structure f
        JOIN payment p ON f.Fee_ID = p.Fee_ID
        WHERE p.Student_ID=%s
    """, (student_id,))
    fees = cursor.fetchall()

    # Receipt
    cursor.execute("""
        SELECT r.*
        FROM receipt r
        JOIN payment p ON r.Payment_ID = p.Payment_ID
        WHERE p.Student_ID=%s
    """, (student_id,))
    receipts = cursor.fetchall()

    return render_template('student_dashboard.html',
                           student=student,
                           payments=payments,
                           fees=fees,
                           receipts=receipts)


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)