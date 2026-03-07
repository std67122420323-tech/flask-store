from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shoes.sqlite' # เก็บไฟล์ไว้ในโฟลเดอร์ instance

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # ถ้ายังไม่ล็อกอิน ให้ดีดกลับไปหน้านี้

from shoe import routes # สำคัญ: ต้อง Import routes จากโฟลเดอร์ shoe