from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from wtforms.validators import EqualTo
from products import products
from sanpham import products1

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String(150), nullable=False)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='orders')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})
    email = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    confirm_password = PasswordField(validators=[InputRequired(), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})
    submit = SubmitField("Đăng Ký")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("Tên người dùng này đã tồn tại. Hãy nhập lại.")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("Email này đã được sử dụng. Hãy nhập lại.")

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Đăng Nhập")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            session.pop('_flashes', None)  # Clear any previous flash messages
            flash('Đăng nhập thành công', 'success')  # Add login success message
            return redirect(url_for('dashboard'))
        flash('Email hoặc mật khẩu không đúng', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công. Vui lòng đăng nhập.', 'success')  # Success flash message
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('_flashes', None)  # Clear any previous flash messages
    flash('Đăng xuất thành công', 'success')  # Only add the logout message
    return redirect(url_for('index'))

# Trang cá nhân
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


# Trang chủ
@app.route('/')
def index():
    new_product = [product for product in products if product['category'] == 'Product']
    new_arrivals = [product for product in products if product['category'] == 'new_arrivals']
    men_products = [product for product in products if product['category'] == 'men']
    women_products = [product for product in products if product['category'] == 'women']
    return render_template('base.html', new_product=new_product, new_arrivals=new_arrivals, men_products=men_products, women_products=women_products)

# Trang sản phẩm
@app.route('/product')
def product_list():
    new_product = [product for product in products1 if product['category'] == 'new']
    men_products = [product for product in products1 if product['category'] == 'men']
    women_products = [product for product in products1 if product['category'] == 'women']
    kids_products = [product for product in products1 if product['category'] == 'kids']
    return render_template('products.html', new_product=new_product, men_products=men_products, women_products=women_products, kids_products=kids_products)

@app.route('/new')
def new_products():
    new_products = [p for p in products1 if p.get('category') == 'new']
    return render_template('new.html', products1=new_products)

@app.route('/men')
def men_products():
    men_products = [p for p in products1 if p.get('category') == 'men']
    return render_template('men.html', products1=men_products)

@app.route('/women')
def women_products():
    women_products = [p for p in products1 if p.get('category') == 'women']
    return render_template('women.html', products1=women_products)

@app.route('/kids')
def kids_products():
    kids_products = [p for p in products1 if p.get('category') == 'kids']
    return render_template('kids.html', products1=kids_products)


# Chi tiết sản phẩm
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((item for item in products1 if item["id"] == product_id), None)
    if product is None:
        return "Product not found", 404
    return render_template('product_detail.html', product=product)


# Thêm sản phẩm vào giỏ hàng
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    product = next((p for p in products1 if p['id'] == product_id), None)
    if not product:
        return "Sản phẩm không tồn tại", 404
    
    if 'cart' not in session or not isinstance(session['cart'], list):
        session['cart'] = []

    cart_item = product.copy()
    price_str = cart_item['price'].replace('.', '').replace(',', '')  # Remove formatting
    cart_item['price_value'] = float(price_str)
    session['cart'].append(cart_item)
    session.modified = True
    return redirect(url_for('cart'))

# Trang giỏ hàng
@app.route('/cart')
def cart():
    # Make sure 'cart' is initialized as an empty list if it's not set or it's not a list
    cart = session.get('cart')
    if cart is None or not isinstance(cart, list):  
        session['cart'] = []  # Ensure cart is an empty list in the session if not set or malformed
        cart = []  # Initialize cart locally as well
    
    valid_cart = [item for item in cart if isinstance(item, dict)]  # Filter valid items
    total = sum(item.get('price_value', 0) for item in valid_cart)  # Calculate total
    
    return render_template('cart.html', cart=valid_cart, total=total)


# Xóa sản phẩm khỏi giỏ hàng
@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'cart' in session:
        session['cart'] = [p for p in session['cart'] if isinstance(p, dict) and p.get('id') != product_id]
        session.modified = True
    return redirect(url_for('cart'))

# Thanh toán
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    total = sum(item.get('price_value', 0) for item in cart)
    estimated_delivery_handling = 0  # Miễn phí giao hàng
    return render_template('checkout.html', cart=cart, total=total, estimated_delivery_handling=estimated_delivery_handling)

# Guest Checkout
@app.route('/guest_checkout', methods=['GET', 'POST'])
def guest_checkout():
    if request.method == 'POST':
        # Lấy dữ liệu từ form
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        payment_method = request.form['payment_method']
    
        # Xử lý thanh toán ở đây (lưu vào cơ sở dữ liệu, gửi email, v.v.)
        flash('Đơn hàng của bạn đã đặt thành công.', 'success')
        return redirect(url_for('index'))
    
    # Tính tổng số tiền từ giỏ hàng trong session
    cart = session.get('cart', [])
    total = sum(item.get('price_value', 0) for item in cart)
    
    return render_template('guest_checkout.html', total=total)

# Member checkout
@app.route('/member_checkout', methods=['GET', 'POST'])
@login_required
def member_checkout():
    cart = session.get('cart', [])
    total = sum(item.get('price_value', 0) for item in cart)

    if request.method == 'POST':
        payment_method = request.form['payment_method']
        # Lưu thông tin đơn hàng vào cơ sở dữ liệu
        new_order = Order(user_id=current_user.id, total_amount=total, payment_method=payment_method)
        db.session.add(new_order)
        db.session.commit()

        flash('Đơn hàng của bạn đã được xử lý và lưu vào lịch sử mua hàng.', 'success')
        session.pop('cart', None)  # Xóa giỏ hàng sau khi đặt hàng thành công
        return redirect(url_for('index'))
    return render_template('member_checkout.html', total=total, user=current_user)

# Lịch sử mua hàng
@app.route('/order_history')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    Order.created_at = datetime.now()
    db.session.commit()
    return render_template('order_history.html', orders=orders)

# Thêm sản phẩm yêu thích
@app.route('/favorites')
@login_required
def favorites():
    favorite_products = db.session.query(Product).join(Favorite, Product.id == Favorite.product_id).filter(Favorite.user_id == current_user.id).all()
    return render_template('favorites.html', products=favorite_products)


@app.route('/add_to_favorite/<int:product_id>')
@login_required
def add_to_favorite(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('index'))
    existing_favorite = Favorite.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if not existing_favorite:
        new_favorite = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(new_favorite)
        db.session.commit()
        flash('Product added to favorites.', 'success')
    else:
        flash('Product is already in your favorites.', 'info')
    return redirect(url_for('product_detail', product_id=product_id))



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

