from flask import Flask, render_template, request, redirect, session
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "my_local_secret_key")

app = Flask(__name__)
app.secret_key = SECRET_KEY

# In-memory mock databases
users = []  # Each user: {'username': ..., 'password': ..., 'role': ...}
appointments = []  # Each appointment: {'patient': ..., 'doctor': ..., 'date': ..., 'time': ...}
diagnoses = []  # Each diagnosis: {'patient': ..., 'doctor': ..., 'notes': ...}

# ---------- Helper Functions (No AWS) ----------

def register_user(username, password, role):
    users.append({'username': username, 'password': password, 'role': role})

def validate_login(username, password):
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user['role']
    return None

def load_users():
    return users

def book_appointment(patient, doctor, date, time):
    appointments.append({'patient': patient, 'doctor': doctor, 'date': date, 'time': time})

def get_user_appointments(username):
    return [a for a in appointments if a['patient'] == username]

def get_doctor_appointments(doctor):
    return [a for a in appointments if a['doctor'] == doctor]

def submit_diagnosis(patient, doctor, notes):
    diagnoses.append({'patient': patient, 'doctor': doctor, 'notes': notes})

def get_doctor_diagnoses(doctor):
    return [d for d in diagnoses if d['doctor'] == doctor]

def get_patient_diagnoses(patient):
    return [d for d in diagnoses if d['patient'] == patient]

# ---------- Routes ----------

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        register_user(data['username'], data['password'], data['role'])
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = validate_login(username, password)
        if role:
            session['username'] = username
            session['role'] = role
            return redirect('/dashboard')
        return "Invalid Credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('dashboard.html', username=session['username'], role=session['role'])

@app.route('/book', methods=['GET', 'POST'])
def book():
    if 'username' not in session:
        return redirect('/')
    if request.method == 'POST':
        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        book_appointment(session['username'], doctor, date, time)
        return redirect('/appointments')
    return render_template('book.html')

@app.route('/appointments')
def appointments_view():
    if 'username' not in session:
        return redirect('/')
    user_appointments = get_user_appointments(session['username'])
    return render_template('appointments.html', appointments=user_appointments)

@app.route('/doctor-appointments')
def doctor_appointments():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect('/')
    appts = get_doctor_appointments(session['username'])
    return render_template('doctor_appointments.html', appointments=appts)

@app.route('/submit-diagnosis', methods=['GET', 'POST'])
def submit_diagnosis_route():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect('/')
    
    if request.method == 'POST':
        patient = request.form['patient']
        notes = request.form['notes']
        submit_diagnosis(patient, session['username'], notes)
        return render_template("diagnosis_success.html")

    patients = [u['username'] for u in load_users() if u['role'] == 'patient']
    return render_template('submit_diagnosis.html', patients=patients)

@app.route('/view-diagnosis')
def view_diagnosis_route():
    if 'username' not in session or session['role'] != 'doctor':
        return redirect('/')
    diagnoses_list = get_doctor_diagnoses(session['username'])
    return render_template('view_diagnosis.html', diagnoses=diagnoses_list)

@app.route('/my-diagnosis')
def my_diagnosis():
    if 'username' not in session or session['role'] != 'patient':
        return redirect('/')
    diagnoses_list = get_patient_diagnoses(session['username'])
    return render_template('my_diagnosis.html', diagnoses=diagnoses_list)

# ---------- Run App Locally ----------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
