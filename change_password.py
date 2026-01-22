#!/usr/bin/env python3
"""
Script to generate a hashed password for the library system
"""

from werkzeug.security import generate_password_hash

def generate_new_password():
    print("🔧 أداة توليد كلمة مرور مشفرة لنظام مكتبة النخبة")
    print("=" * 50)
    
    password = input("أدخل كلمة المرور الجديدة: ")
    confirm_password = input("أعد إدخال كلمة المرور: ")
    
    if password != confirm_password:
        print("❌ كلمتا المرور غير متطابقتين!")
        return
    
    if len(password) < 6:
        print("❌ يجب أن تكون كلمة المرور مكونة من 6 أحرف على الأقل!")
        return
    
    # Generate hash
    password_hash = generate_password_hash(password)
    
    print("\n✅ تم توليد التشفير بنجاح:")
    print(f"\n{password_hash}")
    print("\n" + "=" * 50)
    print("لتحديث كلمة المرور:")
    print("1. انسخ التشفير أعلاه")
    print("2. غيّر متغير ADMIN_PASSWORD_HASH في ملف library_secure.py")
    print("3. استبدل القيمة الحالية بهذه: generate_password_hash('كلمة_المرور_الجديدة')")

if __name__ == "__main__":
    generate_new_password()