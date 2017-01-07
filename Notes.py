from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import SelectField, SubmitField, TextAreaField
import time
from base64 import b64decode
import logging
logging.basicConfig(filename='/home/vengle/FlaskProj/Notes/logs/NotesApp.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s', 
                    datefmt='%m/%d/%Y %I:%M:%S %p')

logging.debug('Starting up....')




app = Flask(__name__)
db = SQLAlchemy(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/vengle/FlaskProj/Notes/NotesDB.sqlite3'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True




class NotesStore(db.Model):
   __tablename__ = "mynotes"
   id    = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(256))
   user  = db.Column(db.String(48))
   note  = db.Column(db.BLOB)  
   ctime = db.Column(db.Integer)
   mtime = db.Column(db.Integer)


class RestoreDB(db.Model):
   __tablename__ = "restoredb"
   id    = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(256))
   user  = db.Column(db.String(48))
   note  = db.Column(db.BLOB)
   ctime = db.Column(db.Integer)
   mtime = db.Column(db.Integer)



def SaveNote(request):
    content = request.form['NoteContent']
    title   = request.form['NoteTitle']
    Author = GetUser(request)
    logging.info("Adding Note By: " + Author)
    # Replace this with real author once issues with login are worked out.
    #Author  = 'vengle'
    c = int(time.time())
    m = int(time.time())
    entry   = NotesStore(title=title,user=Author,note=content,ctime=c,mtime=m)
    db.session.add(entry)
    db.session.commit()
    return (title,content,Author)

def UpdateNote(request):
    logging.info("Updating Note ID: " + str(note_id))
    content = request.form['NoteContent']
    title   = request.form['Title']
    note_id   = request.form['Note_ID']
    author   = request.form['User']
    m = int(time.time())
    result = NotesStore.query.filter(NotesStore.id == note_id).first()
    result.title = title
    result.note=content
    result.mtime=m
    db.session.commit()
    return (title,content,author)

def DeleteNote(note_id):
    logging.info("Deleting from Notes DB, Note ID: " + str(note_id))
    result = NotesStore.query.filter(NotesStore.id == note_id).first()
    c = int(time.time())
    restoreentry   = RestoreDB(id=c,title=result.title,user=result.user,
                     note=result.note,ctime=result.ctime,mtime=result.mtime)
    db.session.add(restoreentry)
    db.session.commit()
    db.session.delete(result)
    db.session.commit()
    # Fix this later. Need to return actual status.
    return ('Delete Success')


def RestoreNote(note_id):
    logging.info("Looking in restore DB for Note ID: " + str(note_id))
    result = RestoreDB.query.filter(RestoreDB.id == note_id).first()
    restoreentry   = NotesStore(title=result.title,user=result.user,
                     note=result.note,ctime=result.ctime,mtime=result.mtime)
    db.session.add(restoreentry)
    db.session.commit()
    db.session.delete(result)
    db.session.commit()
    # Fix this later. Need to return actual status.
    return ('Restore Success')


def GetNote(note_id,tableobj):
    result = tableobj.query.filter(NotesStore.id == note_id).first()
    if result == None:
        return ("Not Found","err","err","0","0")
    Author  = result.user
    ctime = result.ctime
    mtime = result.mtime
    title   = result.title
    content = result.note
    return (title,content,Author,ctime,mtime)

def GetUser(request):
    auth = request.headers["Authorization"]
    userpass = auth.split()[1]
    details = b64decode(userpass)
    fields = details.split(':')
    username = fields[0] 
    return username

@app.route("/view")
@app.route("/view/<note_id>")
def view(note_id=None):
    if note_id == None:
        msg = "No note id provided to /view..."
        return render_template('new_note.html',  msg=msg)
    else:
        (title,content,author,ctime,mtime) = GetNote(note_id,NotesStore)
        c = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ctime))
        m = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        return render_template('viewnote.html', title=title,  
                                 content=content, author=author,
                                 ctime=c, mtime=m, note_id=note_id)

@app.route("/restore")
def restore():
    results = RestoreDB.query.all()
    msg = "Welcome to Notes..."
    return render_template('restore.html', msg=msg, results=results)



@app.route("/edit", methods=['GET','POST'])
@app.route("/edit/<note_id>", methods=['GET','POST'])
def edit(note_id=None):
    if note_id == None:
        if request.method == 'POST':
            (title,content,author) = UpdateNote(request)
            return render_template('viewnote.html', title=title, 
                            content=content, author=author)
        else:
            msg = "No note id provided to /edit..."
            return render_template('new_note.html',  msg=msg)
    else:
        (title,content,author,ctime,mtime) = GetNote(note_id,NotesStore)
        msg = "Editing Note ID: " + note_id
        return render_template('editnote.html', NoteTitle=title,
                                 NoteContent=content, Note_ID=note_id, 
                                 msg=msg, User=author)

@app.route("/delete", methods=['GET','POST'])
@app.route("/delete/<note_id>", methods=['GET','POST'])
def delete(note_id=None):
    if note_id == None:
        msg = "No Note ID Provided. Nothing Deleted..."
        results = NotesStore.query.all()
        return render_template('Main.html', msg=msg, results=results)
    else:
        deleteresult = DeleteNote(note_id)
        results = NotesStore.query.all()
        msg = "Deleted Note ID: " + note_id
        return render_template('Main.html', msg=msg, results=results)


@app.route("/restorenote/<note_id>")
def restorenote(note_id=None):
    if note_id == None:
        msg = "No Note ID Provided. Nothing Deleted..."
        results = NotesStore.query.all()
        return render_template('Main.html', msg=msg, results=results)
    else:
        restoreresult = RestoreNote(note_id)
        results = NotesStore.query.all()
        msg = "Restored Note ID: " + note_id
        return render_template('Main.html', msg=msg, results=results)




@app.route("/new", methods=['GET','POST'])
def new():
    if request.method == 'POST':
        (title,content,author) = SaveNote(request)
        return render_template('viewnote.html', title=title,  
                                 content=content, author=author)
    msg = "Creating a new Note..."
    return render_template('new_note.html',  msg=msg)

@app.route("/")
def hello():
    results = NotesStore.query.all()
    msg = "Welcome to Notes..."
    return render_template('Main.html', msg=msg, results=results)


@app.route("/req", methods=['GET','POST'])
def req():
    auth = request.headers["Authorization"]
    userpass = auth.split()[1]
    details = b64decode(userpass)
    fields = details.split(':')
    username = fields[0]
    return render_template('headers.html',  reqhead=username)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
