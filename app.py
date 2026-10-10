import re
import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_
from models import db, User, Item, ItemMedia, Message, ContactAlias

app = Flask(__name__)
app.config['SECRET_KEY'] = 'campusmart_mvp_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campusmart.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)
VIT_EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@vitstudent\.ac\.in$')

@app.route('/')
def index():
    if 'user_id' not in session: return redirect(url_for('login'))
        
    query = request.args.get('q', '')
    categories = request.args.getlist('category')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)

    item_query = Item.query
    if query: item_query = item_query.filter(or_(Item.title.ilike(f'%{query}%'), Item.description.ilike(f'%{query}%')))
    if categories: item_query = item_query.filter(Item.category.in_(categories))
    if min_price is not None: item_query = item_query.filter(Item.price >= min_price)
    if max_price is not None: item_query = item_query.filter(Item.price <= max_price)

    items = item_query.order_by(Item.id.desc()).all()
    return render_template('index.html', items=items, current_user_id=session['user_id'])

# --- NEW AUTHENTICATION LOGIC ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id') # Can be username or email
        password = request.form.get('password')
        
        user = User.query.filter(or_(User.email == login_id, User.username == login_id)).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            flash("Incorrect credentials. Please check your username/email and password.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not VIT_EMAIL_REGEX.match(email):
            flash("Unauthorized: Please use your @vitstudent.ac.in email.", "danger")
            return redirect(url_for('register'))
            
        if User.query.filter_by(email=email).first():
            flash("Email is already in use.", "danger")
            return redirect(url_for('register'))
            
        if User.query.filter_by(username=username).first():
            flash("Username is already taken.", "danger")
            return redirect(url_for('register'))
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- ITEM LOGIC ---
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    new_item = Item(
        title=request.form.get('title'), description=request.form.get('description', ''),
        price=request.form.get('price'), category=request.form.get('category'),
        user_id=session['user_id']
    ) 
    db.session.add(new_item)
    db.session.flush()
    
    files = request.files.getlist('images')
    has_images = False
    for file in files:
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            db.session.add(ItemMedia(item_id=new_item.id, filename=filename))
            has_images = True
            
    if not has_images: db.session.add(ItemMedia(item_id=new_item.id, filename='default.jpg'))
    db.session.commit()
    flash("Item listed successfully!", "success")
    return redirect(url_for('index'))

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    item = Item.query.get_or_404(item_id)
    return render_template('item.html', item=item, current_user_id=session['user_id'])

@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    item = Item.query.get_or_404(item_id)
    if item.user_id != session['user_id']:
        flash("Unauthorized.", "danger")
        return redirect(url_for('index'))
        
    db.session.delete(item)
    db.session.commit()
    flash("Action successful. The listing has been removed.", "success")
    return redirect(url_for('profile', user_id=session['user_id']))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    items = Item.query.filter_by(user_id=user_id).order_by(Item.id.desc()).all()
    alias_record = ContactAlias.query.filter_by(user_id=session['user_id'], contact_id=user_id).first()
    display_name = alias_record.alias if alias_record else user.username
    return render_template('profile.html', profile_user=user, items=items, display_name=display_name, current_user_id=session['user_id'])

# --- INBOX & CHAT ROUTES ---
@app.route('/inbox')
def inbox():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('inbox.html')

@app.route('/api/inbox_contacts')
def api_inbox_contacts():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    current_user_id = session['user_id']
    messages = Message.query.filter(or_(Message.sender_id == current_user_id, Message.receiver_id == current_user_id)).order_by(Message.timestamp.desc()).all()
    contact_ids = []
    for msg in messages:
        other_id = msg.sender_id if msg.receiver_id == current_user_id else msg.receiver_id
        if other_id not in contact_ids: contact_ids.append(other_id)
    contacts_data = []
    for cid in contact_ids:
        user = User.query.get(cid)
        alias_record = ContactAlias.query.filter_by(user_id=current_user_id, contact_id=cid).first()
        unread_count = Message.query.filter_by(sender_id=cid, receiver_id=current_user_id, is_read=False).count()
        # Fallback to username instead of email
        contacts_data.append({'id': cid, 'display_name': alias_record.alias if alias_record else user.username, 'email': user.username, 'has_unread': unread_count > 0})
    return jsonify({'status': 'success', 'data': contacts_data})

@app.route('/api/set_alias', methods=['POST'])
def api_set_alias():
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    record = ContactAlias.query.filter_by(user_id=session['user_id'], contact_id=data.get('contact_id')).first()
    if record: record.alias = data.get('alias')
    else: db.session.add(ContactAlias(user_id=session['user_id'], contact_id=data.get('contact_id'), alias=data.get('alias')))
    db.session.commit()
    return jsonify({'status': 'success'})

@app.route('/chat/<int:receiver_id>')
def chat(receiver_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    if session['user_id'] == receiver_id: return redirect(url_for('index'))
    receiver = User.query.get_or_404(receiver_id)
    alias = ContactAlias.query.filter_by(user_id=session['user_id'], contact_id=receiver_id).first()
    return render_template('chat.html', receiver=receiver, display_name=alias.alias if alias else receiver.username, current_user_id=session['user_id'])

@app.route('/api/messages/<int:receiver_id>', methods=['GET', 'POST'])
def api_messages(receiver_id):
    if 'user_id' not in session: return jsonify({'error': 'Unauthorized'}), 401
    sender_id = session['user_id']
    if request.method == 'POST':
        content = request.get_json().get('content')
        if content:
            db.session.add(Message(sender_id=sender_id, receiver_id=receiver_id, content=content))
            db.session.commit()
            return jsonify({'status': 'success'})
        return jsonify({'error': 'Empty message'}), 400
    unread = Message.query.filter_by(sender_id=receiver_id, receiver_id=sender_id, is_read=False).all()
    for u in unread: u.is_read = True
    if unread: db.session.commit()
    messages = Message.query.filter(((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) | ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))).order_by(Message.timestamp.asc()).all()
    return jsonify({"status": "success", "data": [{"sender_id": m.sender_id, "content": m.content, "timestamp": m.timestamp.strftime('%Y-%m-%d %H:%M:%S')} for m in messages]})

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)
