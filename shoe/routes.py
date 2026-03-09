import os
from flask import render_template, redirect, url_for, request, flash
from shoe import app, db
from shoe.models import User, Shoe, ShoeImage
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'shoe/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@app.route('/index')
def index():
    search = request.args.get('search', '')
    if search:
        shoes = Shoe.query.filter(
            (Shoe.model.contains(search)) | (Shoe.brand.contains(search))
        ).all()
    else:
        shoes = Shoe.query.all()
    return render_template('index.html', shoes=shoes, search_query=search, title="KodFlow Collection")

@app.route('/shoe/<int:shoe_id>')
def shoe_detail(shoe_id):
    shoe = Shoe.query.get_or_404(shoe_id)
    return render_template('shoe_detail.html', shoe=shoe, title=shoe.model)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        file = request.files.get('file_img')
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"user_{current_user.id}.{ext}")
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            current_user.profile_img = url_for('static', filename=f'profile_pics/{filename}')

        new_profile_url = request.form.get('profile_img')
        if new_profile_url and not file:
            current_user.profile_img = new_profile_url
            
        if new_username and new_username != current_user.username:
            if not User.query.filter_by(username=new_username).first():
                current_user.username = new_username
        
        if new_password:
            current_user.password = generate_password_hash(new_password)
            
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('profile.html', title="Profile Settings")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'warning')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title="Join KodFlow")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Login Unsuccessful', 'danger')
    return render_template('login.html', title="Login")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_shoe', methods=['GET', 'POST'])
@login_required
def add_shoe():
    if request.method == 'POST':
        try:
            new_shoe = Shoe(
                model=request.form.get('model'),
                brand=request.form.get('brand'),
                price=float(request.form.get('price')),
                size=request.form.get('size'), 
                shirt_size=request.form.get('shirt_size'),  
                img=request.form.get('img'), 
                user_id=current_user.id
            )
            db.session.add(new_shoe)
            db.session.flush()

            extra_imgs = request.form.get('extra_imgs', '').splitlines()
            for url in extra_imgs:
                if url.strip():
                    new_img = ShoeImage(img_url=url.strip(), shoe_id=new_shoe.id)
                    db.session.add(new_img)

            db.session.commit()
            flash('เพิ่มสินค้าเรียบร้อยแล้ว!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
    return render_template('add_shoe.html', shoe=None, title="Add New Shoe")

@app.route('/update_shoe/<int:shoe_id>', methods=['GET', 'POST'])
@login_required
def update_shoe(shoe_id):
    shoe = Shoe.query.get_or_404(shoe_id)
    if shoe.user_id != current_user.id:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        shoe.model = request.form.get('model')
        shoe.brand = request.form.get('brand')
        shoe.price = float(request.form.get('price'))
        shoe.size = request.form.get('size') 
        shoe.shirt_size = request.form.get('shirt_size')  
        shoe.img = request.form.get('img') 

        ShoeImage.query.filter_by(shoe_id=shoe.id).delete()
        extra_imgs = request.form.get('extra_imgs', '').splitlines()
        for url in extra_imgs:
            if url.strip():
                new_img = ShoeImage(img_url=url.strip(), shoe_id=shoe.id)
                db.session.add(new_img)

        db.session.commit()
        flash('แก้ไขข้อมูลสำเร็จ!', 'success')
        return redirect(url_for('index'))
    
    current_extra_imgs = "\n".join([img.img_url for img in shoe.additional_images])
    return render_template('add_shoe.html', shoe=shoe, extra_imgs=current_extra_imgs, title="Edit Shoe")

@app.route('/delete_shoe/<int:shoe_id>', methods=['POST'])
@login_required
def delete_shoe(shoe_id):
    shoe = Shoe.query.get_or_404(shoe_id)
    if shoe.user_id == current_user.id:
        db.session.delete(shoe)
        db.session.commit()
        flash('Shoe deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/checkout/<int:shoe_id>', methods=['POST'])
@login_required
def checkout(shoe_id):
    shoe = Shoe.query.get_or_404(shoe_id)
    selected_size = request.form.get('selected_size')
    
    if not selected_size or selected_size == "None":
        flash('กรุณาเลือกไซส์ก่อนสั่งซื้อ', 'warning')
        return redirect(url_for('shoe_detail', shoe_id=shoe.id))
        
    return render_template('checkout.html', shoe=shoe, size=selected_size, title="Checkout")