from CRUD import CRUD
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_wtf import Form
from wtforms import TextField, SubmitField, TextAreaField
import time
from base64 import b64decode
import logging
from fortune import FortuneTools
import markdown
import pygments

fort = FortuneTools()
fort.LoadFortunes()

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
app.secret_key = "I hate to tell you"


class SearchForm(Form):
   searchkey = TextField("Search")

class NotesStore(db.Model):
   __tablename__ = "mynotes"
   id    = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(256))
   user  = db.Column(db.String(48))
   note  = db.Column(db.Text(8196))
   ctime = db.Column(db.Integer)
   mtime = db.Column(db.Integer)


class RestoreDB(db.Model):
   __tablename__ = "restoredb"
   id    = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(256))
   user  = db.Column(db.String(48))
   note  = db.Column(db.Text(8196))
   ctime = db.Column(db.Integer)
   mtime = db.Column(db.Integer)

dbutil = CRUD(db, NotesStore, RestoreDB,logging)

@app.route("/view")
@app.route("/view/<note_id>")
def view(note_id=None):
    if note_id == None:
        msg = "No note id provided to /view..."
        return render_template('new_note.html',  msg=msg)
    else:
        (title,content,author,ctime,mtime) = dbutil.GetNote(note_id,NotesStore)
        converted2html = markdown.markdown(content, extensions = ['codehilite'])
        return render_template('viewnote-v2.html', title=title,  
                                 content=converted2html, author=author,
                                 ctime=ctime, mtime=mtime, note_id=note_id)

@app.route("/restore")
def restore():
    results = RestoreDB.query.all()
    msg = "Recover a Deleted Note..."
    return render_template('restore.html', msg=msg, results=results)



@app.route("/edit", methods=['GET','POST'])
@app.route("/edit/<note_id>", methods=['GET','POST'])
def edit(note_id=None):
    if note_id == None:
        if request.method == 'POST':
            (title,content,author,note_id,mtime,ctime) = dbutil.UpdateNote(request)
            converted2html = markdown.markdown(content, extensions = ['codehilite'])
            return render_template('viewnote-v2.html', title=title, 
                            content=converted2html, author=author, note_id=note_id,
                            mtime=mtime, ctime=ctime)
        else:
            msg = "No note id provided to /edit..."
            return render_template('new_note.html',  msg=msg)
    else:
        (title,content,author,ctime,mtime) = dbutil.GetNote(note_id,NotesStore)
        msg = "Editing Note ID: " + note_id
        return render_template('editnote.html', NoteTitle=title,
                                 NoteContent=content, Note_ID=note_id, 
                                 msg=msg, User=author, mtime=mtime, ctime=ctime)

@app.route("/delete", methods=['GET','POST'])
@app.route("/delete/<note_id>", methods=['GET','POST'])
def delete(note_id=None):
    if note_id == None:
        msg = "No Note ID Provided. Nothing Deleted..."
        results = NotesStore.query.all()
        search = SearchForm()
        return render_template('Main.html', search=search, msg=msg, results=results)
    else:
        deleteresult = dbutil.DeleteNote(note_id)
        search = SearchForm()
        results = NotesStore.query.all()
        msg = "Deleted Note ID: " + note_id
        return render_template('Main.html', search=search, msg=msg, results=results)


@app.route("/restorenote/<note_id>")
def restorenote(note_id=None):
    if note_id == None:
        msg = "No Note ID Provided. Nothing Deleted..."
        results = NotesStore.query.all()
        search = SearchForm()
        return render_template('Main.html', search=search, msg=msg, results=results)
    else:
        restoreresult = dbutil.RestoreNote(note_id)
        results = NotesStore.query.all()
        search = SearchForm()
        msg = "Restored Note ID: " + note_id
        return render_template('Main.html', search=search, msg=msg, results=results)




@app.route("/new", methods=['GET','POST'])
def new():
    if request.method == 'POST':
        (title,content,author,note_id,mtime,ctime) = dbutil.SaveNote(request)
        converted2html = markdown.markdown(content, extensions = ['codehilite'])
        return render_template('viewnote-v2.html', title=title,  
                                 content=converted2html, author=author, note_id=note_id)
    msg = "Creating a new Note..."
    return render_template('new_note.html',  msg=msg)


@app.route("/")
def hello():
    results = NotesStore.query.all()
    msg = "Welcome to Notes..."
    search = SearchForm()
    return render_template('Main.html', search=search, msg=msg, results=results)


@app.route("/search", methods=['GET','POST'])
def search():
    keyword = request.form['searchkey']
    key = '%{}%'.format(keyword.strip())
    results = NotesStore.query.filter(or_(NotesStore.note.like(key) ,NotesStore.title.like(key))).all()
    msg = "Search Results for: " + keyword
    search = SearchForm()
    return render_template('Main.html', search=search, msg=msg, results=results)


@app.route("/req", methods=['GET','POST'])
def req():
    auth = request.headers["Authorization"]
    userpass = auth.split()[1]
    details = b64decode(userpass)
    fields = details.split(':')
    username = fields[0]
    return render_template('headers.html',  reqhead=username)

@app.route("/fortune")
def fortune():
    fortunecookie = fort.GetRandom()
    return render_template('fortune.html', fortunecookie=fortunecookie)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
