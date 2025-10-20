import sqlite3
import os
import hashlib

# 🔧 Đảm bảo file users.db nằm cùng cấp với thư mục core
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(_file_), ".."))
USER_DB = os.path.join(BASE_DIR, "users.db")


def init_user_db():
    """Khởi tạo CSDL người dùng và tạo admin mặc định nếu chưa có"""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            is_active INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    # ✅ Tạo tài khoản admin mặc định nếu chưa có
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
        c.execute(
            "INSERT INTO users (username, password, role, status, is_active) VALUES (?, ?, ?, ?, ?)",
            ("admin", admin_pass, "admin", "active", 0)
        )
        print("✅ Admin mặc định được tạo: admin / admin123")

    conn.commit()
    conn.close()


def hash_password(password: str):
    """Mã hóa mật khẩu"""
    return hashlib.sha256(password.encode()).hexdigest()


def register(username: str, password: str):
    """Đăng ký người dùng mới"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, role, status, is_active) VALUES (?, ?, ?, ?, ?)",
            (username, hash_password(password), 'user', 'active', 0)
        )
        conn.commit()
        print(f"🆕 User mới được tạo: {username}")
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login(username: str, password: str):
    """Đăng nhập: trả về thông tin người dùng nếu hợp lệ, cập nhật trạng thái hoạt động"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    user = c.fetchone()
    if not user:
        conn.close()
        return None

    # Kiểm tra nếu tài khoản bị khóa
    if len(user) >= 5 and user[4] == 'locked':
        conn.close()
        return 'locked'

    # ✅ Cập nhật trạng thái hoạt động
    c.execute("UPDATE users SET is_active=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()
    return user


def logout_user(username: str):
    """Cập nhật trạng thái is_active = 0 khi người dùng đăng xuất"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()


def toggle_user_status(user_id: int):
    """Khóa hoặc mở khóa người dùng (trừ admin)"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT status FROM users WHERE id=? AND username!='admin'", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
    new_status = 'locked' if row[0] == 'active' else 'active'
    c.execute("UPDATE users SET status=? WHERE id=? AND username!='admin'", (new_status, user_id))
    conn.commit()
    conn.close()
    return True


def delete_user(user_id: int):
    """Xóa người dùng (trừ admin)"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=? AND username!='admin'", (user_id,))
    conn.commit()
    conn.close()
    return True


def get_all_users():
    """Trả về danh sách tất cả người dùng"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("SELECT id, username, role, status, is_active FROM users")
    users = c.fetchall()
    conn.close()
    return users


def set_user_active(username: str, active: bool):
    """Cập nhật trạng thái hoạt động (is_active = 1 hoặc 0)"""
    conn = sqlite3.connect(USER_DB)
    c = conn.cursor()
    c.execute("UPDATE users SET is_active=? WHERE username=?", (1 if active else 0, username))
    conn.commit()
    conn.close()