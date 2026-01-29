from flask import Flask, request, render_template, url_for, redirect, session, jsonify
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

engine = create_engine('sqlite:///user_notes.db')

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    mail_id = Column(String)

class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    n_title = Column(String(400))
    n_content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
 

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

app = Flask(__name__)
app.secret_key = "kkk"

@app.route('/', methods = ['GET','POST'])
def home():
    if request.method == 'POST':
        mail = request.form['email']
        usr_name = request.form['user']
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        
        if pass1 != pass2:
            return f"Password don't match!"
            
        else:
            new_user = User(
                user_name = usr_name,
                password = pass2,
                mail_id = mail
            )
            db.add(new_user)
            db.commit()
            
            return redirect(url_for('login'))
        
    return render_template('sign.html')
        
        
@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        lg_usr = request.form['user']
        lg_psd = request.form['pass']
        
        log_check = db.query(User).filter(
            User.user_name == lg_usr
        ).first()
        
        if not log_check:
            return f"Wrong Username"
        elif log_check.password != lg_psd:
            return f"Wrong Password"
        else:
            session["user_id"] = log_check.id
            return redirect(url_for('notes'))
    
    return render_template('login.html')
        
        
@app.route('/notes', methods = ['GET','POST'])
def notes():
    
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))
    

    
    user_notes = db.query(Note).filter(
        Note.user_id == user_id
    ).order_by(Note.created_at.desc()).all()
    
    if request.method == 'POST':
        create_btn = request.form['note_button']
        if create_btn == "create":
            return redirect(url_for('create_note_page'))
    
    return render_template('notes.html', notes=user_notes)
        
        
@app.route('/api/create_new_note', methods = ['POST'])
def create_note():
    user_id = session.get("user_id")
    if not user_id:
        return "Not Logged In!!!",401
        
    data = request.json

    note = Note(
        n_title=data["title"],
        n_content=data["content"],
        user_id=user_id
    )

        
    db.add(note)
    db.commit()
        
    return {
        "id": note.id,
        "title": note.n_title,
        "content": note.n_content,
        "created_at": note.created_at.isoformat()
    }
    

@app.route('/create', methods=['GET'])
def create_note_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))

    return render_template('create_note.html')


@app.route('/api/delete/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()
    
    if not note:
        return "Not Allowed", 403
        
    db.delete(note)
    db.commit()
    
    return {"success":True}
 
@app.route("/note/<int:id>")
def note_page(id):
	return render_template("single_note.html", note_id=id)

@app.route("/api/note/<int:note_id>")
def get_note(note_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for('login'))
        
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == user_id).first()
    if not note:
        return "Not Allowed", 403
        
    data ={
		"title": note.n_title,
		"content": note.n_content,
        "time": note.created_at.strftime("%d %b %Y, %I:%M %p")
        }
    return jsonify(data)

 
if __name__ == '__main__':
    app.run(debug=True)