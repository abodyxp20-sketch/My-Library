import sys
import subprocess
import json
import os
import datetime
import io
import webbrowser
from threading import Timer

# تثبيت المكتبات اللازمة تلقائياً
try:
    from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_file
    import pandas as pd
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "pandas", "openpyxl"])
    from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, send_file

app = Flask(__name__)
app.secret_key = "super_secret_key_999"

# إعدادات النظام
ADMIN_PASSWORD = "admin"  # غيّرها إذا أردت
DATA_FILE = "library_pro_data.json"
BORROW_RECORDS_FILE = "borrow_records.json"

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
        const data = {
            studentName: document.getElementById('studentName').value,
            bookId: document.getElementById('bookId').value,
            bookTitle: document.getElementById('bookTitle').value,
            bookCategory: document.getElementById('bookCategory').value,
            borrowDate: document.getElementById('borrowDate').value,
            returnDate: document.getElementById('returnDate').value,
            notes: document.getElementById('notes').value || "لا توجد ملاحظات"
        };
        if (!data.studentName) return alert("يرجى إدخال اسم الطالب");
        
        const res = await fetch('/api/save_borrow', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (result.success) {
            alert("تم تسجيل طلب الاستعارة بنجاح!");
            location.reload();
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

# --- منطق السيرفر ---
def load_records():
    if os.path.exists(BORROW_RECORDS_FILE):
        with open(BORROW_RECORDS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_records(data):
    with open(BORROW_RECORDS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
    if request.form.get('pass') == ADMIN_PASSWORD:
        session['is_admin'] = True
        return redirect(url_for('admin'))
    return render_template_string(HTML_TEMPLATE, page='admin_login', error=True)

@app.route('/admin/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/api/save_borrow', methods=['POST'])
def save_borrow():
    data = request.json
    records = load_records()
    data['id'] = str(datetime.datetime.now().timestamp())
    records.append(data)
    save_records(records)
    return jsonify({"success": True})

@app.route('/api/get_records')
def get_records():
    if not session.get('is_admin'):
        return jsonify([])
    return jsonify(load_records())

@app.route('/api/delete/<id>', methods=['DELETE'])
def delete_record(id):
    if not session.get('is_admin'):
        return jsonify({"success": False})
    records = [r for r in load_records() if r['id'] != id]
    save_records(records)
    return jsonify({"success": True})

@app.route('/export_excel')
def export_excel():
    if not session.get('is_admin'):
        return "Access Denied", 403
    df = pd.DataFrame(load_records())
    if df.empty:
        df = pd.DataFrame(columns=["studentName", "bookTitle", "bookCategory", "borrowDate", "returnDate", "notes"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="سجلات الاستعارة")
    output.seek(0)
    return send_file(output, download_name="Library_Elite_Report.xlsx", as_attachment=True)

if __name__ == '__main__':
    print("🚀 نظام المكتبة النخبة يعمل الآن بكفاءة عالية...")
    Timer(1, lambda: webbrowser.open('http://127.0.0.1:5000')).start()
    app.run(port=5000, debug=False)