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
        return (title,content,Author,result.id, self.FormatTime(result.mtime),
                self.FormatTime(result.ctime))


    def GetUser(self,request):
        auth = request.headers["Authorization"]
        userpass = auth.split()[1]
        details = b64decode(userpass)
        fields = details.split(':')
        username = fields[0]
        return username


    def UpdateNote(self,request):
        content = request.form['NoteContent']
        title   = request.form['Title']
        note_id   = request.form['Note_ID']
        self.logging.info("Updating Note ID: " + str(note_id))
        author   = request.form['User']
        m = int(time.time())
        result = self.NotesStore.query.filter(self.NotesStore.id == note_id).first()
        result.title = title
        result.note=content
        result.mtime=m
        self.db.session.commit()
        return (title, content, author, result.id, self.FormatTime(m), 
                self.FormatTime(result.ctime))


    def DeleteNote(self,note_id):
        self.logging.info("Deleting from Notes DB, Note ID: " + str(note_id))
        result = self.NotesStore.query.filter(self.NotesStore.id == note_id).first()
        c = int(time.time())
        restoreentry   = self.RestoreDB(id=c,title=result.title,user=result.user,
                         note=result.note, ctime=result.ctime,
                         mtime=result.mtime)
        self.db.session.add(restoreentry)
        self.db.session.commit()
        self.db.session.delete(result)
        self.db.session.commit()
        # Fix this later. Need to return actual status.
        return ('Delete Success')


    def RestoreNote(self,note_id):
        self.logging.info("Looking in restore DB for Note ID: " + str(note_id))
        result = self.RestoreDB.query.filter(self.RestoreDB.id == note_id).first()
        restoreentry   = self.NotesStore(title=result.title,user=result.user,
                         note=result.note,ctime=result.ctime,mtime=result.mtime)
        self.db.session.add(restoreentry)
        self.db.session.commit()
        self.db.session.delete(result)
        self.db.session.commit()
        # Fix this later. Need to return actual status.
        return ('Restore Success')


    def GetNote(self,note_id,tableobj):
        result = tableobj.query.filter(tableobj.id == note_id).first()
        if result == None:
            return ("Not Found","err","err","0","0")
        Author  = result.user
        ctime = result.ctime
        mtime = result.mtime
        title   = result.title
        content = result.note
        return (title,content,Author,self.FormatTime(ctime),
                self.FormatTime(mtime))



    def FormatTime(self,t):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
