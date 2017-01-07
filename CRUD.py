from base64 import b64decode
import time



class CRUD:

    def __init__(self, db, NotesStore, RestoreDB,logging):
        self.db = db
        self.NotesStore = NotesStore
        self.RestoreDB = RestoreDB
        self.logging = logging


    def SaveNote(self,request):
        content = request.form['NoteContent']
        title   = request.form['NoteTitle']
        Author  = self.GetUser(request)
        self.logging.info("Adding Note By: " + Author)
        c = int(time.time())
        m = int(time.time())
        entry   = self.NotesStore(title=title,user=Author,note=content,ctime=c,mtime=m)
        self.db.session.add(entry)
        self.db.session.commit()
        result = self.NotesStore.query.filter(self.NotesStore.ctime == c).first()
        return (title,content,Author,result.id)


    def GetUser(self,request):
        auth = request.headers["Authorization"]
        userpass = auth.split()[1]
        details = b64decode(userpass)
        fields = details.split(':')
        username = fields[0]
        return username

