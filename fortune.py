from Utils import Files
import time, random



class FortuneTools:

    def __init__(self):
        self.fortunefile = '/home/vengle/projects/Notes/fortunes.txt'
        self.fortunes = dict()


    def LoadFortunes(self):
        f = Files()
        f.read_file(self.fortunefile)
        myfortune = ''
        i = 4000
        for line in f.data:
            x = line.strip()
            if x == '%':
                self.fortunes[i] = myfortune
                i += 1
                myfortune = ''
            else:
                myfortune = myfortune + line + "\n"
                
    def GetRandom(self):
        mylist = self.fortunes.keys()
        mykey = random.choice (mylist)
        return self.fortunes[mykey]

    def FormatTime(self,t):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t))
