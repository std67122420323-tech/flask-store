from shoe import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile_img = db.Column(db.String(500), nullable=True, default='https://cdn-icons-png.flaticon.com/512/149/149071.png')
    shoes = db.relationship('Shoe', backref='owner', lazy=True)

class Shoe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    size = db.Column(db.Float, nullable=False) 
    shirt_size = db.Column(db.String(10), nullable=True) 
    
    
    additional_images = db.relationship('ShoeImage', backref='shoe', lazy=True, cascade="all, delete-orphan")

class ShoeImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img_url = db.Column(db.String(500), nullable=False)
    shoe_id = db.Column(db.Integer, db.ForeignKey('shoe.id'), nullable=False)