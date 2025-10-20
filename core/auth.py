from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("⚠️ Hãy đăng nhập trước khi truy cập.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash("⚠️ Hãy đăng nhập.")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("🚫 Chỉ admin mới có quyền truy cập trang này.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated