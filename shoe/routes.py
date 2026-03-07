from flask import render_template, redirect, url_for, request, flash
from shoe import app, db
from shoe.models import User, Shoe
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. หน้าหลักและการค้นหา ---
@app.route('/')
@login_required
def index():
    """แสดงรายการรองเท้าทั้งหมดของผู้ใช้ และระบบค้นหา"""
    search = request.args.get('search', '')
    if search:
        # ค้นหาเฉพาะรองเท้าที่เป็นของ User คนที่ล็อกอินอยู่
        user_shoes = Shoe.query.filter(
            Shoe.user_id == current_user.id,
            (Shoe.model.contains(search)) | (Shoe.brand.contains(search))
        ).all()
    else:
        user_shoes = Shoe.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', shoes=user_shoes, search_query=search, title="Home")

# --- 2. การจัดการข้อมูลรองเท้า (CRUD) ---
@app.route('/add_shoe', methods=['GET', 'POST'])
@login_required
def add_shoe():
    """เพิ่มข้อมูลรองเท้าใหม่"""
    if request.method == 'POST':
        try:
            new_shoe = Shoe(
                model=request.form.get('model'),
                brand=request.form.get('brand'),
                price=float(request.form.get('price')),
                size=float(request.form.get('size')),
                img=request.form.get('img'), 
                user_id=current_user.id
            )
            db.session.add(new_shoe)
            db.session.commit()
            flash('เพิ่มข้อมูลรองเท้าเรียบร้อย!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback() # ย้อนกลับหากเกิดข้อผิดพลาดในการบันทึก
            flash(f'เกิดข้อผิดพลาด: {str(e)}', 'danger')
    return render_template('add_shoe.html', shoe=None, title="เพิ่มรองเท้าใหม่")

@app.route('/update_shoe/<int:shoe_id>', methods=['GET', 'POST'])
@login_required
def update_shoe(shoe_id):
    """แก้ไขข้อมูลรองเท้า (เฉพาะของตัวเอง)"""
    shoe = Shoe.query.get_or_404(shoe_id)
    
    # ตรวจสอบสิทธิ์ความเป็นเจ้าของก่อนแก้ไข
    if shoe.user_id != current_user.id:
        flash('คุณไม่มีสิทธิ์แก้ไขรายการนี้', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            shoe.model = request.form.get('model')
            shoe.brand = request.form.get('brand')
            shoe.price = float(request.form.get('price'))
            shoe.size = float(request.form.get('size'))
            shoe.img = request.form.get('img') 
            db.session.commit()
            flash('อัปเดตข้อมูลเรียบร้อย!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการอัปเดต: {str(e)}', 'danger')
            
    return render_template('add_shoe.html', shoe=shoe, title="แก้ไขข้อมูลรองเท้า")

@app.route('/delete_shoe/<int:shoe_id>', methods=['POST'])
@login_required
def delete_shoe(shoe_id):
    """ลบข้อมูลรองเท้า (เฉพาะของตัวเอง)"""
    shoe = Shoe.query.get_or_404(shoe_id)
    if shoe.user_id == current_user.id:
        db.session.delete(shoe)
        db.session.commit()
        flash('ลบข้อมูลเรียบร้อยแล้ว', 'info')
    else:
        flash('คุณไม่มีสิทธิ์ลบรายการนี้', 'danger')
    return redirect(url_for('index'))

# --- 3. ระบบสมาชิก (Authentication) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    """สมัครสมาชิกใหม่"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('ชื่อผู้ใช้นี้มีคนใช้แล้ว กรุณาเลือกชื่ออื่น', 'warning')
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="สมัครสมาชิก")

@app.route('/login', methods=['GET', 'POST'])
def login():
    """เข้าสู่ระบบ"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')
    return render_template('login.html', title="เข้าสู่ระบบ")

@app.route('/logout')
def logout():
    """ออกจากระบบ"""
    logout_user()
    return redirect(url_for('login'))

# --- 4. ระบบจัดการโปรไฟล์ ---
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """ตั้งค่าโปรไฟล์และเปลี่ยนรหัสผ่าน"""
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        
        # ตรวจสอบชื่อผู้ใช้ซ้ำ (กรณีเปลี่ยนชื่อใหม่)
        if new_username and new_username != current_user.username:
            user_check = User.query.filter_by(username=new_username).first()
            if user_check:
                flash('ชื่อผู้ใช้นี้ถูกใช้งานแล้ว', 'warning')
            else:
                current_user.username = new_username
        
        # เปลี่ยนรหัสผ่าน (ถ้ามีการกรอกมา)
        if new_password:
            current_user.password = generate_password_hash(new_password)
        
        db.session.commit()
        flash('อัปเดตโปรไฟล์สำเร็จ', 'success')
        return redirect(url_for('profile'))
    return render_template('profile.html', title="ตั้งค่าโปรไฟล์")