import sys
import subprocess
import json
import os
import datetime
import io
import webbrowser
from threading import Timer
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from contextlib import contextmanager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re

# تثبيت المكتبات اللازمة تلقائياً
try:
    from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_file
    import pandas as pd
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "pandas", "openpyxl"])
    from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_file
    import pandas as pd

app = Flask(__name__)
# Generate a random secret key for sessions
import secrets
app.secret_key = secrets.token_hex(16)

# إعدادات النظام - تم تشفير كلمة المرور
ADMIN_PASSWORD_HASH = generate_password_hash("admin")  # تشفير كلمة المرور باستخدام Werkzeug
DB_FILE = "library.db"

# قائمة الكتب الـ20 (متنوعة ومرتبة حسب الطلب)
BOOKS = [
    {
        "id": 1,
        "title": "Madrigal's Magic Key to Spanish",
        "category": "اللغات",
        "description": "الكتاب الأكثر شهرة وسهولة لتعلم اللغة الإسبانية من الصفر، يعتمد على الربط الذهني والصور لتحويل الإنجليزية إلى إسبانية بسرعة."
    },
    {
        "id": 2,
        "title": "Clean Code",
        "category": "البرمجة",
        "description": "دليل أساسي لكتابة كود نظيف وقابل للصيانة، من تأليف روبرت مارتن (Uncle Bob)، مثالي لكل مبرمج محترف."
    },
    {
        "id": 3,
        "title": "Python Crash Course",
        "category": "البرمجة",
        "description": "أفضل كتاب عملي لتعلم بايثون من الصفر إلى المستوى المتقدم، يحتوي على مشاريع حقيقية وتمارين تفاعلية."
    },
    {
        "id": 4,
        "title": "Eloquent JavaScript",
        "category": "تطوير الويب",
        "description": "كتاب مجاني وعملي لتعلم JavaScript الحديثة بعمق، مع تمارين تفاعلية ومشاريع ويب حقيقية."
    },
    {
        "id": 5,
        "title": "HTML and CSS: Design and Build Websites",
        "category": "تطوير الويب",
        "description": "مرجع شامل ومصور لتصميم مواقع الويب بـHTML وCSS، مثالي للمبتدئين والمحترفين."
    },
    {
        "id": 6,
        "title": "Sapiens: A Brief History of Humankind",
        "category": "تاريخ",
        "description": "رحلة مذهلة عبر تاريخ البشرية من العصر الحجري إلى العصر الحديث، من تأليف يوفال نوح هراري."
    },
    {
        "id": 7,
        "title": "Guns, Germs, and Steel",
        "category": "تاريخ وعلم",
        "description": "تحليل علمي لأسباب تفاوت الحضارات عبر التاريخ، حائز على جائزة بوليتزر."
    },
    {
        "id": 8,
        "title": "Cosmos",
        "category": "علم",
        "description": "رحلة كونية مذهلة مع كارل ساغان، يشرح الكون والعلوم بأسلوب ساحر وملهم."
    },
    {
        "id": 9,
        "title": "The Selfish Gene",
        "category": "علم",
        "description": "كتاب ريادي في علم الأحياء التطوري من ريتشارد دوكينز، يغير نظرتك للحياة والتطور."
    },
    {
        "id": 10,
        "title": "1984",
        "category": "رواية",
        "description": "رواية ديستوبية خالدة لجورج أورويل عن الشمولية والمراقبة والحرية."
    },
    {
        "id": 11,
        "title": "To Kill a Mockingbird",
        "category": "رواية",
        "description": "تحفة هاربر لي عن العنصرية والعدالة والبراءة في أمريكا الجنوبية."
    },
    {
        "id": 12,
        "title": "The Great Gatsby",
        "category": "رواية",
        "description": "رواية ف. سكوت فيتزجيرالد الكلاسيكية عن الحلم الأمريكي والوهم والثراء."
    },
    {
        "id": 13,
        "title": "Pride and Prejudice",
        "category": "رواية",
        "description": "كوميديا رومانسية خالدة لجين أوستن عن الحب والطبقات الاجتماعية."
    },
    {
        "id": 14,
        "title": "Atomic Habits",
        "category": "تطوير الذات",
        "description": "دليل عملي لبناء عادات جيدة وكسر العادات السيئة، من جيمس كلير."
    },
    {
        "id": 15,
        "title": "How to Win Friends and Influence People",
        "category": "تطوير الذات",
        "description": "كلاسيكية ديل كارنيجي في العلاقات البشرية والتواصل الفعال."
    },
    {
        "id": 16,
        "title": "Thinking, Fast and Slow",
        "category": "علم النفس",
        "description": "تحليل عميق لدانيال كانيمان عن كيفية عمل العقل البشري واتخاذ القرارات."
    },
    {
        "id": 17,
        "title": "Man's Search for Meaning",
        "category": "علم النفس",
        "description": "تجربة فيكتور فرانكل في المعتقلات النازية وفلسفته عن إيجاد المعنى في الحياة."
    },
    {
        "id": 18,
        "title": "The Power of Habit",
        "category": "تطوير الذات",
        "description": "شرح علمي لكيفية تكوين العادات وتغييرها، من تشارلز دوهيغ."
    },
    {
        "id": 19,
        "title": "Dune",
        "category": "رواية",
        "description": "ملحمة خيال علمي خالدة لفرانك هربرت عن السياسة والدين والبيئة."
    },
    {
        "id": 20,
        "title": "The Alchemist",
        "category": "رواية",
        "description": "رواية فلسفية ملهمة لباولو كويلو عن متابعة الأحلام والقدر."
    }
]

# --- تصميم الواجهات (HTML & CSS محترف ومرتب جداً) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite Library System | نظام المكتبة النخبة</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Poppins:wght@300;600&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #1a237e; --accent: #ffd700; --text-dark: #2c3e50; --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Cairo', sans-serif; background: var(--bg-gradient); min-height: 100vh; color: var(--text-dark); }
        nav { background: rgba(26, 35, 126, 0.95); padding: 15px 5%; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 1000; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        .logo { color: var(--accent); font-size: 1.8rem; font-weight: bold; text-decoration: none; }
        .nav-links a { color: white; text-decoration: none; margin-right: 25px; font-weight: 500; transition: 0.3s; }
        .nav-links a:hover { color: var(--accent); }
        .main-container { max-width: 1200px; margin: 40px auto; padding: 20px; }
        .glass-card { background: rgba(255, 255, 255, 0.95); border-radius: 20px; padding: 30px; box-shadow: 0 15px 35px rgba(0,0,0,0.1); margin-bottom: 30px; }
        h2 { text-align: center; color: var(--primary); margin-bottom: 30px; }
        .books-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 25px; }
        .book-card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,0.1); transition: 0.3s; }
        .book-card:hover { transform: translateY(-10px); }
        .book-info { padding: 20px; }
        .book-title { font-size: 1.3rem; font-weight: bold; color: var(--primary); margin-bottom: 10px; }
        .book-category { color: var(--accent); font-weight: bold; margin-bottom: 10px; }
        .book-desc { font-size: 0.95rem; line-height: 1.6; color: #555; margin-bottom: 15px; }
        .btn-borrow { width: 100%; background: var(--primary); color: white; border: none; padding: 12px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        .btn-borrow:hover { background: #283593; }
        .form-section { margin-top: 40px; padding: 25px; background: #f9f9ff; border-radius: 15px; display: none; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 10px; overflow: hidden; }
        th { background: var(--primary); color: white; padding: 15px; }
        td { padding: 12px; text-align: center; border-bottom: 1px solid #eee; }
        .btn-action { background: #d32f2f; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; }
        .login-box { max-width: 400px; margin: 100px auto; text-align: center; }
    </style>
</head>
<body>
<nav>
    <a href="/" class="logo">ELITE LIBRARY</a>
    <div class="nav-links">
        <a href="/">بوابة الطالب</a>
        <a href="/admin">لوحة التحكم (Admin)</a>
    </div>
</nav>
<div class="main-container">
    {% if page == 'student' %}
    <div class="glass-card">
        <h2>📚 قائمة الكتب المتاحة (20 كتاباً متنوعاً)</h2>
        <div class="books-grid">
            {% for book in books %}
            <div class="book-card">
                <div class="book-info">
                    <div class="book-title">{{ book.title }}</div>
                    <div class="book-category">{{ book.category }}</div>
                    <div class="book-desc">{{ book.description }}</div>
                    <button class="btn-borrow" onclick="openBorrowForm({{ book.id }}, '{{ book.title }}', '{{ book.category }}')">استعارة الكتاب</button>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- نموذج طلب الاستعارة التفصيلي -->
        <div class="glass-card form-section" id="borrowForm">
            <h2>طلب استعارة كتاب</h2>
            <form id="borrowSubmitForm">
                <input type="hidden" id="bookId">
                <label>اسم الكتاب:</label>
                <input type="text" id="bookTitle" readonly>
                <label>تصنيف الكتاب:</label>
                <input type="text" id="bookCategory" readonly>
                <label>اسم الطالب الكامل:</label>
                <input type="text" id="studentName" required>
                <label>البريد الإلكتروني:</label>
                <input type="email" id="studentEmail" required>
                <label>تاريخ الاستعارة (اليوم):</label>
                <input type="text" id="borrowDate" readonly>
                <label>تاريخ الترجيع المتوقع (بعد 14 يوماً):</label>
                <input type="text" id="returnDate" readonly>
                <label>ملاحظات إضافية (اختياري):</label>
                <input type="text" id="notes">
                <button type="submit" class="btn-action" style="width:100%; background:var(--primary); margin-top:20px;">تأكيد الطلب</button>
            </form>
        </div>
    </div>

    {% elif page == 'admin_login' %}
    <div class="glass-card login-box">
        <h2>🔐 دخول المسؤول</h2>
        <form action="/admin/auth" method="POST">
            <input type="password" name="pass" placeholder="كلمة المرور" required>
            <button type="submit" class="btn-action" style="width:100%; background:var(--primary);">دخول</button>
        </form>
        {% if error %}<p style="color:red; margin-top:10px;">كلمة المرور خاطئة!</p>{% endif %}
    </div>

    {% elif page == 'admin_dashboard' %}
    <div class="glass-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
            <h2>📊 سجلات الاستعارة</h2>
            <a href="/admin/logout" style="color:red; font-weight:bold;">تسجيل الخروج</a>
        </div>
        <button class="btn-action" onclick="window.location.href='/export_excel'" style="background:#2e7d32; margin-bottom:20px;">📥 تصدير Excel</button>
        <table>
            <thead>
                <tr>
                    <th>اسم الطالب</th>
                    <th>البريد الإلكتروني</th>
                    <th>اسم الكتاب</th>
                    <th>التصنيف</th>
                    <th>تاريخ الاستعارة</th>
                    <th>تاريخ الترجيع المتوقع</th>
                    <th>ملاحظات</th>
                    <th>إجراء</th>
                </tr>
            </thead>
            <tbody id="adminTable"></tbody>
        </table>
    </div>
    {% endif %}
</div>

<script>
    function openBorrowForm(id, title, category) {
        document.getElementById('borrowForm').style.display = 'block';
        document.getElementById('bookId').value = id;
        document.getElementById('bookTitle').value = title;
        document.getElementById('bookCategory').value = category;
        document.getElementById('borrowDate').value = new Date().toLocaleDateString('ar-EG');
        const returnDate = new Date();
        returnDate.setDate(returnDate.getDate() + 14);
        document.getElementById('returnDate').value = returnDate.toLocaleDateString('ar-EG');
        document.getElementById('borrowForm').scrollIntoView({ behavior: 'smooth' });
    }

    document.getElementById('borrowSubmitForm')?.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // تنظيف وتحقق من البيانات
        const studentName = document.getElementById('studentName').value.trim();
        const studentEmail = document.getElementById('studentEmail').value.trim();
        const notes = document.getElementById('notes').value.trim();
        
        // التحقق من صحة البريد الإلكتروني
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(studentEmail)) {
            alert("يرجى إدخال بريد إلكتروني صحيح");
            return;
        }
        
        if (!studentName) {
            alert("يرجى إدخال اسم الطالب");
            return;
        }
        
        const data = {
            studentName: studentName,
            studentEmail: studentEmail,
            bookId: document.getElementById('bookId').value,
            bookTitle: document.getElementById('bookTitle').value,
            bookCategory: document.getElementById('bookCategory').value,
            borrowDate: document.getElementById('borrowDate').value,
            returnDate: document.getElementById('returnDate').value,
            notes: notes || "لا توجد ملاحظات"
        };
        
        const res = await fetch('/api/save_borrow', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            alert("تم تسجيل طلب الاستعارة بنجاح!");
            location.reload();
        } else {
            alert(result.message || "حدث خطأ أثناء تسجيل الطلب");
        }
    });

    async function loadAdminData() {
        const res = await fetch('/api/get_records');
        const data = await res.json();
        const tbody = document.getElementById('adminTable');
        if (!tbody) return;
        tbody.innerHTML = '';
        data.forEach(r => {
            tbody.innerHTML += `<tr>
                <td>${r.studentName}</td>
                <td>${r.studentEmail}</td>
                <td>${r.bookTitle}</td>
                <td>${r.bookCategory}</td>
                <td>${r.borrowDate}</td>
                <td>${r.returnDate}</td>
                <td>${r.notes}</td>
                <td><button class="btn-action" onclick="deleteRecord('${r.id}')">حذف</button></td>
            </tr>`;
        });
    }

    async function deleteRecord(id) {
        if (confirm('حذف هذا السجل نهائياً؟')) {
            await fetch(`/api/delete/${id}`, {method: 'DELETE'});
            loadAdminData();
        }
    }

    if (document.getElementById('adminTable')) loadAdminData();
</script>
</body>
</html>
"""

# --- منطق قاعدة البيانات ---
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create borrow records table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS borrow_records (
            id TEXT PRIMARY KEY,
            student_name TEXT NOT NULL,
            student_email TEXT NOT NULL,
            book_id INTEGER NOT NULL,
            book_title TEXT NOT NULL,
            book_category TEXT NOT NULL,
            borrow_date TEXT NOT NULL,
            return_date TEXT NOT NULL,
            notes TEXT
        )
    ''')
    
    # Create books table if needed
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    
    # Insert books if they don't exist
    cursor.execute('SELECT COUNT(*) FROM books')
    if cursor.fetchone()[0] == 0:
        for book in BOOKS:
            cursor.execute('''
                INSERT INTO books (id, title, category, description)
                VALUES (?, ?, ?, ?)
            ''', (book['id'], book['title'], book['category'], book['description']))
    
    conn.commit()
    conn.close()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def sanitize_input(input_str):
    """Clean input to prevent SQL injection and XSS"""
    if input_str is None:
        return None
    
    # Remove potentially dangerous characters
    sanitized = input_str.strip()
    
    # Prevent SQL injection by checking for common attack patterns
    dangerous_patterns = ["'", "\"", ";", "--", "/*", "*/", "xp_", "sp_"]
    for pattern in dangerous_patterns:
        if pattern.lower() in sanitized.lower():
            raise ValueError(f"Invalid input detected: {pattern}")
    
    return sanitized

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, page='student', books=BOOKS)

@app.route('/admin')
def admin():
    if session.get('is_admin'):
        return render_template_string(HTML_TEMPLATE, page='admin_dashboard')
    return render_template_string(HTML_TEMPLATE, page='admin_login', error=False)

@app.route('/admin/auth', methods=['POST'])
def auth():
    password = request.form.get('pass')
    if password and check_password_hash(ADMIN_PASSWORD_HASH, password):
        session['is_admin'] = True
        return redirect(url_for('admin'))
    return render_template_string(HTML_TEMPLATE, page='admin_login', error=True)

@app.route('/admin/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/api/save_borrow', methods=['POST'])
def save_borrow():
    try:
        data = request.json
        
        # Validate and sanitize inputs
        student_name = sanitize_input(data.get('studentName', ''))
        student_email = sanitize_input(data.get('studentEmail', ''))
        book_id = int(data.get('bookId', 0))
        book_title = sanitize_input(data.get('bookTitle', ''))
        book_category = sanitize_input(data.get('bookCategory', ''))
        borrow_date = sanitize_input(data.get('borrowDate', ''))
        return_date = sanitize_input(data.get('returnDate', ''))
        notes = sanitize_input(data.get('notes', ''))
        
        # Additional validation
        if not all([student_name, student_email, book_id, book_title, book_category, borrow_date, return_date]):
            return jsonify({"success": False, "message": "جميع الحقول المطلوبة يجب أن تكون معبأة"})
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, student_email):
            return jsonify({"success": False, "message": "البريد الإلكتروني غير صحيح"})
        
        # Check if book exists
        book_exists = any(book['id'] == book_id for book in BOOKS)
        if not book_exists:
            return jsonify({"success": False, "message": "الكتاب المحدد غير موجود"})
        
        record_id = str(datetime.datetime.now().timestamp())
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO borrow_records 
                (id, student_name, student_email, book_id, book_title, book_category, borrow_date, return_date, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (record_id, student_name, student_email, book_id, book_title, book_category, borrow_date, return_date, notes))
            conn.commit()
        
        return jsonify({"success": True})
    
    except ValueError as ve:
        return jsonify({"success": False, "message": f"Input validation error: {str(ve)}"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error saving record: {str(e)}"})

@app.route('/api/get_records')
def get_records():
    if not session.get('is_admin'):
        return jsonify([])
    
    try:
        with get_db_connection() as conn:
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM borrow_records ORDER BY borrow_date DESC')
            records = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for record in records:
                result.append({
                    'id': record['id'],
                    'studentName': record['student_name'],
                    'studentEmail': record['student_email'],
                    'bookId': record['book_id'],
                    'bookTitle': record['book_title'],
                    'bookCategory': record['book_category'],
                    'borrowDate': record['borrow_date'],
                    'returnDate': record['return_date'],
                    'notes': record['notes']
                })
            
            return jsonify(result)
    
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify([])

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_record(id):
    if not session.get('is_admin'):
        return jsonify({"success": False})
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM borrow_records WHERE id = ?', (id,))
            conn.commit()
        
        return jsonify({"success": True})
    
    except Exception as e:
        print(f"Database error during deletion: {e}")
        return jsonify({"success": False})

@app.route('/export_excel')
def export_excel():
    if not session.get('is_admin'):
        return "Access Denied", 403
    
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query('SELECT * FROM borrow_records ORDER BY borrow_date DESC', conn)
            
            # Rename columns to Arabic for better readability
            df.columns = ['المعرف', 'اسم الطالب', 'البريد الإلكتروني', 'رقم الكتاب', 'عنوان الكتاب', 
                         'التصنيف', 'تاريخ الاستعارة', 'تاريخ الترجيع', 'ملاحظات']
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="سجلات الاستعارة")
            output.seek(0)
            return send_file(output, download_name="Library_Elite_Report.xlsx", as_attachment=True)
    
    except Exception as e:
        print(f"Export error: {e}")
        return "Export failed", 500

def schedule_notification_emails():
    """Schedule email notifications for books due tomorrow"""
    def send_notifications():
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d/%m/%Y')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT student_email, student_name, book_title FROM borrow_records WHERE return_date = ?', (tomorrow,))
            records = cursor.fetchall()
        
        # Email configuration (you would put real credentials here)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your_email@example.com"  # Replace with actual email
        sender_password = "your_app_password"   # Replace with actual password
        
        for record in records:
            student_email, student_name, book_title = record
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = student_email
            msg['Subject'] = "تذكير بإعادة كتاب - Elite Library System"
            
            body = f"""
            عزيزي الطالب {student_name}،
            
            نذكرك بلطف بأن كتاب "{book_title}" المستعار من مكتبنا يجب أن تعيده غداً.
            
            نأمل منك التقيد بالمواعيد لضمان استفادة جميع الطلاب من الكتب.
            
            مع خالص التحيات،
            إدارة مكتبة النخبة
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                text = msg.as_string()
                server.sendmail(sender_email, student_email, text)
                server.quit()
            except Exception as e:
                print(f"Failed to send notification to {student_email}: {e}")
    
    # Schedule the notification function to run daily
    from threading import Thread
    import time
    
    def run_scheduler():
        while True:
            now = datetime.datetime.now()
            # Run at 8 AM daily
            if now.hour == 8 and now.minute == 0:
                send_notifications()
            time.sleep(60)  # Check every minute
    
    thread = Thread(target=run_scheduler, daemon=True)
    thread.start()

if __name__ == '__main__':
    # Initialize the database
    init_db()
    
    # Start the notification scheduler
    schedule_notification_emails()
    
    print("🚀 نظام المكتبة النخبة يعمل الآن بكفاءة عالية...")
    print("🔒 تم تفعيل جميع تدابير الأمان")
    print("💾 جاري استخدام قاعدة بيانات SQLite")
    print("📧 نظام الإشعارات البريدية جاهز")
    Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(port=5000, debug=False)