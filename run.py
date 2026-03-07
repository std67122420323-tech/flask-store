from shoe import app, db  # เปลี่ยนจาก epl เป็น shoe

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # สร้างฐานข้อมูลอัตโนมัติถ้ายังไม่มี
    app.run(debug=True, host='0.0.0.0') # รันโหมด Debug เพื่อดู Error ได้ง่าย