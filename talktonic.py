# ...existing code...
from flask import Flask, request, redirect, url_for, render_template_string, jsonify
import sqlite3
import os
from datetime import datetime
from talk_tonic.spoken_english.english import spoken_english

DB_PATH = os.path.join(os.path.dirname(__file__), "talktonic.db")

COURSES = {
    "spoken-english": {
        "title": "Spoken English",
        "overview": "Improve fluency, pronunciation and confidence for real-world conversations.",
        "benefits": ["Conversation practice", "Pronunciation drills", "Interview prep"],
        "syllabus": ["Basics & Phonetics", "Daily conversations", "Public speaking"],
        "duration": "8 weeks",
        "price": "₹4,999"
    },
    "python-training": {
        "title": "Python Training",
        "overview": "Hands-on Python training from basics to intermediate with projects.",
        "benefits": ["Hands-on labs", "Real-world projects", "Placement support"],
        "syllabus": ["Syntax & Data types", "OOP", "Web & Data projects"],
        "duration": "10 weeks",
        "price": "₹9,999"
    },
    "dsa-training": {
        "title": "DSA Training",
        "overview": "Data structures & algorithms with competitive programming practice.",
        "benefits": ["Problem solving", "Interview patterns", "Mock interviews"],
        "syllabus": ["Arrays & Strings", "Trees & Graphs", "Dynamic Programming"],
        "duration": "12 weeks",
        "price": "₹12,999"
    }
}

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        course_id TEXT,
        status TEXT DEFAULT 'pending',
        created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, email TEXT, message TEXT, created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, created_at TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS testimonials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, role TEXT, message TEXT, created_at TEXT
    )""")
    conn.commit()
    conn.close()

app = Flask(__name__)
app.register_blueprint(spoken_english)
init_db()

BASE_HTML = """
<!doctype html>
<title>TalkTonic</title>
<style>
 body{font-family:Segoe UI, Roboto, Arial; margin: 0; padding: 0;}
 .hero{background:#0b76ef;color:white;padding:40px;text-align:center}
 .container{padding:20px;max-width:900px;margin:0 auto}
 .card{border:1px solid #eee;padding:16px;margin:10px 0;border-radius:6px}
 .cta{display:inline-block;padding:10px 16px;background:#ff7a59;color:white;border-radius:4px;text-decoration:none}
</style>
<div class="hero">
  <h1>TalkTonic — Learn. Build. Grow.</h1>
  <p>Spoken English • Python • DSA • Resume & LinkedIn help</p>
  <a class="cta" href="{{ url_for('register') }}">Join Now</a>
</div>
<div class="container">
  {% block body %}{% endblock %}
  <hr>
  <footer style="font-size:90%;">Contact: contact@talktonic.example | Follow: LinkedIn · Instagram · YouTube</footer>
</div>
"""

@app.route("/")
def index():
    courses = COURSES
    body = """
    <h2>Our Courses</h2>
    {% for cid, c in courses.items() %}
      <div class="card">
        <h3>{{ c.title }}</h3>
        <p>{{ c.overview }}</p>
        <p><strong>Duration:</strong> {{ c.duration }} &nbsp; <strong>Price:</strong> {{ c.price }}</p>
        <a href="{{ url_for('course_page', course_id=cid) }}">View course</a>
      </div>
    {% endfor %}
    <h2>Testimonials</h2>
    {% for t in testimonials %}
      <div class="card"><strong>{{ t.name }}</strong> — {{ t.role }}<p>{{ t.message }}</p></div>
    {% else %}
      <p>No testimonials yet.</p>
    {% endfor %}
    """
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, role, message FROM testimonials ORDER BY id DESC LIMIT 3")
    testimonials = cur.fetchall()
    conn.close()
    return render_template_string(BASE_HTML, courses=courses, testimonials=testimonials, body=body)

@app.route("/course/<course_id>")
def course_page(course_id):
    c = COURSES.get(course_id)
    if not c:
        return "Course not found", 404
    body = """
    <h2>{{ c.title }}</h2>
    <p>{{ c.overview }}</p>
    <p><strong>Duration:</strong> {{ c.duration }} • <strong>Price:</strong> {{ c.price }}</p>
    <h4>Benefits</h4><ul>{% for b in c.benefits %}<li>{{ b }}</li>{% endfor %}</ul>
    <h4>Syllabus Highlights</h4><ul>{% for s in c.syllabus %}<li>{{ s }}</li>{% endfor %}</ul>
    <a class="cta" href="{{ url_for('register', course=course_id) }}">Register for this course</a>
    """
    return render_template_string(BASE_HTML, c=c, course_id=course_id, body=body)

@app.route("/register", methods=["GET", "POST"])
def register():
    course_pref = request.args.get("course", "")
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        course_id = request.form.get("course_id")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO registrations (name,email,course_id,created_at) VALUES (?,?,?,?)",
                    (name, email, course_id, datetime.utcnow().isoformat()))
        reg_id = cur.lastrowid
        conn.commit()
        conn.close()
        # In real app: redirect to payment gateway (Stripe/Razorpay/PayPal) integration point
        return redirect(url_for("payment", reg_id=reg_id))
    body = """
    <h2>Register</h2>
    <form method="post">
      <label>Name</label><br><input name="name" required><br>
      <label>Email</label><br><input name="email" type="email" required><br>
      <label>Course</label><br>
      <select name="course_id">
        {% for cid, c in courses.items() %}
          <option value="{{ cid }}" {% if cid==course_pref %}selected{% endif %}>{{ c.title }} — {{ c.price }}</option>
        {% endfor %}
      </select><br><br>
      <button type="submit">Proceed to Payment</button>
    </form>
    """
    return render_template_string(BASE_HTML, courses=COURSES, course_pref=course_pref, body=body)

@app.route("/login")
def login():
    reason = request.args.get("reason")
    message = "Your assessment shows that guided practice will help you progress faster."
    if reason == "admission":
        message = "Nisha recommends joining Nisha Talk Tonic Institute. Start your admission below."
    body = f"<h2>Student Login</h2><p>{message}</p><p>New to TalkTonic? Use the registration form to begin your admission.</p><a class=\"cta\" href=\"{url_for('register', course='spoken-english')}\">Start admission</a>"
    return render_template_string(BASE_HTML, body=body)

@app.route("/admissions")
def admissions():
    return redirect(url_for("register", course="spoken-english", score=request.args.get("score", "")))

@app.route("/payment")
def payment():
    reg_id = request.args.get("reg_id")
    if not reg_id:
        return "Missing registration id", 400
    # Simulated payment flow: mark registration as paid
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE registrations SET status='paid' WHERE id=?", (reg_id,))
    conn.commit()
    conn.close()
    return render_template_string(BASE_HTML, body=f"<h2>Payment successful</h2><p>Registration #{reg_id} is confirmed.</p>")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO contacts (name,email,message,created_at) VALUES (?,?,?,?)",
                    (name, email, message, datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        return render_template_string(BASE_HTML, body="<h2>Thanks — we'll get back to you shortly.</h2>")
    body = """
    <h2>Contact Us</h2>
    <form method="post">
      <label>Name</label><br><input name="name" required><br>
      <label>Email</label><br><input name="email" type="email" required><br>
      <label>Message</label><br><textarea name="message" required></textarea><br>
      <button type="submit">Send</button>
    </form>
    """
    return render_template_string(BASE_HTML, body=body)

@app.route("/subscribe", methods=["POST"])
def subscribe():
    data = request.get_json() or request.form
    email = data.get("email")
    if not email:
        return jsonify({"error": "email required"}), 400
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subscribers (email, created_at) VALUES (?,?)", (email, datetime.utcnow().isoformat()))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return jsonify({"status": "subscribed"})

@app.route("/blog")
def blog():
    body = "<h2>Blog & Resources</h2><p>Articles, tips and guides coming soon.</p>"
    return render_template_string(BASE_HTML, body=body)

@app.route("/testimonials")
def testimonials():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name, role, message, created_at FROM testimonials ORDER BY id DESC")
    items = cur.fetchall()
    conn.close()
    body = "<h2>Testimonials</h2>"
    for t in items:
        body += f"<div class='card'><strong>{t['name']}</strong> — {t['role']}<p>{t['message']}</p></div>"
    if not items:
        body += "<p>No testimonials yet.</p>"
    return render_template_string(BASE_HTML, body=body)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
# ...existing code...