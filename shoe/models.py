from shoe import db, login_manager  # แก้ไขจาก frfrom เป็น from
from flask_login import UserMixin

# ฟังก์ชันสำหรับดึงข้อมูลผู้ใช้เข้าสู่ระบบ
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ตารางผู้ใช้งาน (User)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # เชื่อมความสัมพันธ์ (User 1 คน : Shoe หลายคู่)
    shoes = db.relationship('Shoe', backref='owner', lazy=True, cascade="all, delete-orphan")

# ตารางรองเท้า (Shoe)
class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    size = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(500)) 
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)