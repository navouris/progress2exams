# NMA June 2020 v 0.3 windows enabled, improved interface of steps 2 and 3
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import webbrowser
import json
import checkExams
import sys

# https://stackoverflow.com/questions/60937345/how-to-set-up-relative-paths-to-make-a-portable-exe-build-in-pyinstaller-with-p
def resource_path(path):
    if getattr(sys, "frozen", False):
        # If the 'frozen' flag is set, we are in bundled-app mode!
        resolved_path = os.path.abspath(os.path.join(sys._MEIPASS, path))
    else:
        # Normal development mode. Use os.getcwd() or __file__ as appropriate in your case...
        resolved_path = os.path.abspath(os.path.join(os.getcwd(), path))

    return resolved_path

print("the home dir is ...", resource_path("."))

class MyApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.backgrColor = "#40423f"
        self.borderColor = "#f5b53f"
        self.title("checkExams v.1")
        self.state = "0"
        self.activeCourse = Course.loadCourses()
        # print("loaded...", self.activeCourse.dir, self.activeCourse.progressFile)
        loadingResult =""
        if self.activeCourse: 
            loadingResult = checkExams.Enrolled.load(self.activeCourse.dir, self.activeCourse.progressFile) # load course data
            # print("result=", loadingResult, "dir, progressFile ==", self.activeCourse.dir, self.activeCourse.progressFile)
        else: loadingResult = False
        if self.activeCourse: print(self.activeCourse.name)
        self.canvas = tk.Canvas(self, width= 1000, height=750)
        self.canvas.pack(expand=True)
        # bakcground images for different states
        # self.canvas.intro = tk.PhotoImage(file= os.path.join(os.path.join(homedir, "media"), "intro.gif"))
        self.canvas.intro = tk.PhotoImage(file= os.path.join(os.path.join(resource_path(""), "media"), "intro.gif"))
        self.canvas.menu = tk.PhotoImage(file= os.path.join(os.path.join(resource_path(""), "media"), "menu.gif"))
        self.canvas.step1 = tk.PhotoImage(file= os.path.join(os.path.join(resource_path(""), "media"), "step1.gif"))
        self.canvas.step2 = tk.PhotoImage(file= os.path.join(os.path.join(resource_path(""), "media"), "step2.gif"))
        self.canvas.step3 = tk.PhotoImage(file= os.path.join(os.path.join(resource_path(""), "media"), "step3.gif"))
        self.states = ["0", "m", "1", "2", "3"] # relate states to background images
        self.stateImages = {"0": self.canvas.intro, "m": self.canvas.menu, "1": self.canvas.step1, \
            "2": self.canvas.step2, "3": self.canvas.step3}
        self.background = self.canvas.create_image(0,0, image=self.canvas.intro, anchor='nw') #εικόνα
        self.renderItems = [] # list of items to render on the canvas on top of the background image
        self.resizable(False, False)
        if loadingResult != "ok":
            if not loadingResult: loadingResult = ""
            self.error("Προσοχή δεν βρέθηκαν δεδομένα του μαθήματος, πρέπει να ορίσετε το μάθημα:"+loadingResult)
        self.homePage()
        # if loadingResult: messagebox.showinfo('loaded', "Τα δεδομένα {} φοιτητών που έχουν εγγραφεί στην εξέταση του μαθήματος {} έχουν καταγραφεί ..."\
        #         .format(len(checkExams.Enrolled.students), self.activeCourse.name))
        # else: messagebox.showinfo('no course', "Δεν υπάρχουν δεδομένα μαθήματος πηγαίνετε στο βήμα 1 ...")
    
    def error(self, text):
        messagebox.showerror("error", text)

    def homePage(self, event=""):
        self.state = "0"
        self.resetState()
        self.nextArrow(self.buildMenu, "menu")
        self.renderItems.append(self.round_rectangle(673, 600, 790, 715, outline=self.backgrColor, fill="", tags = "info"))
        self.canvas.tag_bind("info", '<1>', lambda e : webbrowser.open("https://hci.ece.upatras.gr/progress2exams.html", new=0, autoraise=True))
        # self.drawCourse()
        # print('home page...', self.renderItems, self.canvas.find_all())
    
    def nextArrow(self, binding, tag=""):
        self.renderItems.append(self.round_rectangle(840, 600, 955, 715, outline=self.backgrColor, fill="", tags = tag))
        self.canvas.tag_bind(tag, '<1>', binding)

    def backArrow(self, binding, tag = ""):
        self.renderItems.append(self.round_rectangle(60, 600, 175, 715, outline=self.backgrColor, fill="", tags = tag))
        self.canvas.tag_bind(tag, '<1>', binding)

    def menuBox(self, x, y, binding, tag = ""):
        Dx, Dy = 135,115
        self.renderItems.append(self.round_rectangle(x, y, x+Dx, y+Dy, outline=self.backgrColor, fill="", tags = tag))
        self.canvas.tag_bind(tag, '<1>', binding)        
    
    def drawCourse(self, reset=False):
        if reset:
            self.canvas.delete("course-name")
        self.renderItems.append(self.canvas.create_text(50,185, text= "μαθημα: ", fill=self.borderColor, \
            font = ("Calibri", 40), anchor='nw', tags = "course-name") )
        if self.activeCourse: course = self.activeCourse.name
        else: course = 20*"."
        self.renderItems.append(self.canvas.create_text(230,185, text= course, fill="white", \
            font = ("Calibri", 40), anchor='nw', tags = "course-name") )

    def resetState(self):
        for item in self.renderItems:
            self.canvas.delete(item)
        self.renderItems = []
        self.canvas.itemconfig(self.background, image = self.stateImages[self.state])

    def buildMenu(self, event): # build the main menu card
        print(event)
        print(self.canvas.find_all())
        
        self.state = "m"
        self.resetState()
        # draw course name
        self.drawCourse()
        # draw menu
        x1,y1 =  55, 310
        menuDX = 260
        menuDY = 2225
        nextMenu = 330
        bindings = [self.step1, self.step2, self.step3]
        for i in range(3):
            self.round_rectangle(x1+i*nextMenu, y1, x1 + i*nextMenu+menuDX, y1+menuDY,
                fill="", outline=self.backgrColor, tag="step"+str(i+1))
            self.canvas.tag_bind("step"+str(i+1), "<1>", bindings[i])
        self.backArrow(self.homePage, "home")
        self.nextArrow(self.step1, "step1")
        
    def step1(self, event=""):
        self.state = "1"
        self.resetState()
        self.backArrow(self.buildMenu, "menu")
        self.menuBox(220, 600, self.exams, "exams")
        self.menuBox(400, 600, self.progress, "progress")
        self.menuBox(575, 600, self.course, "course")
        self.nextArrow(self.step2, "step2")
        self.drawCourse()
        print("step1", event)

    def exams(self, event=""):
        webbrowser.open("https://exams.eclass.upatras.gr", new=0, autoraise=True)
        return True

    def progress(self, event=""):
        webbrowser.open("https://progress.upatras.gr", new=0, autoraise=True)
        return True

    def course(self, event=""):
        print('course entered')
        self.activeCourse = Course.loadCourses(setCourse="True")
        if self.activeCourse: 
            self.drawCourse(reset=True)
            checkExams.Enrolled.load(self.activeCourse.dir, self.activeCourse.progressFile)
        print(self.activeCourse)

    def step2(self, event=""):
        self.state = "2"
        self.resetState()
        self.shownContent = ""
        self.backArrow(self.step1, "step1")
        self.menuBox(220, 600, self.check, "check")
        # self.menuBox(400, 600, self.saveFile, "save")
        self.menuBox(400, 600, lambda e: self.saveFile(e, kind="not-eligible"), "save")
        self.menuBox(575, 600, self.sendEmail, "email")
        self.nextArrow(self.step3, "step3")
        self.drawCourse()

    def check(self, event=""):
        # here we check of eligibility
        if self.activeCourse:
            self.displayData(kind="not eligible", exams=True)
        else:
            self.error("Προσοχή πρέπει να ορίσετε μάθημα στο βήμα 1")
    
    def displayData(self, kind="not eligible", exams=False):
        self.fStudent = tk.Frame(self.canvas, relief="groove", borderwidth=2)
        self.fStudent.pack(expand=1, padx=2, pady=2)
        self.menu = tk.Frame(self.fStudent, relief = "groove")
        self.menu.pack(expand=1, fill='both', padx=2, pady=2)
        tk.Label(self.menu, bg=self.backgrColor, fg=self.borderColor, borderwidth=2, text="     Στοιχεία φοιτητών   ", \
                font="Consolas 26").pack(expand=1, fill="both", side="left")
        self.menuButton = tk.Label(self.menu, bg=self.backgrColor, borderwidth=5, fg=self.borderColor, text=" [x] ", font="Consolas 30", width=30)
        self.menuButton.pack(expand=1, fill="both", side="right")
        self.menuButton.bind("<1>", self.removeDataDisplay)
        self.data = tk.Frame(self.fStudent, relief = "groove")
        self.data.pack(expand=1, fill='both')
        self.renderItems.append(self.canvas.create_window(400,0, window= self.fStudent, anchor='nw', width=600, height=750, tags="window")) #παράθυρο μέσα στον καμβά
        self.showStudents = tk.Text(self.data, bg=self.backgrColor)
        self.showStudents.pack(expand=1, fill="both", padx=2, pady=2 )
        self.showStudents.config(font="Consolas 12", fg="white", spacing1=5)
        self.shownContent = checkExams.Enrolled.showStudents(kind = kind, exams=exams)
        self.showStudents.insert(1.0, self.shownContent)

    def removeDataDisplay(self, event=""):
        self.canvas.delete("window")

    def sendEmail(self, event=""):
        if self.activeCourse:
            recipients = checkExams.Enrolled.emailsNotEligible()
            subject = "Διαγραφή σας από την εξέταση στο μάθημα"+self.activeCourse.name 
            body  = '''\nΑγαπητοί φοιτητές,
    μετά από έλεγχο που έγινε διαπιστώσαμε ότι δεν έχετε δικαίωμα 
    να συμμετάσχετε στην εξέταση του μαθήματος, κατά συνέπεια θα διαγραφείτε 
    από την εξέταση του μαθήματος στην πλατφόρμα exams.eclass.upatras.gr
    Αν η διαγραφή αυτή γίνεται από λάθος στον έλεγχο, παρακαλούμε όπως
    έλθετε σε άμεση επαφή μαζί μας.
    Οι διδάσκοντες'''
            messagebox.showinfo(title="email", message="ΠΑΡΑΔΕΙΓΜΑ ΜΗΝΥΜΑΤΟΣ email\n" + body)
            # webbrowser.open('mailto:?to=' + recipients + '&subject=' + subject + '&body=' + body, new=1) #TODO encode in MIME
            webbrowser.open('mailto:?to=' + recipients + '&subject=' + " " + '&body=' + " ", new=1)

    def saveFile(self, event="", kind="not-eligible"):
        if not self.shownContent: self.shownContent = checkExams.Enrolled.showStudents(kind = kind, exams=True)
        outfile = filedialog.asksaveasfile(mode='w', defaultextension=".txt", initialfile = "{}-{}.txt".format(self.activeCourse.name, kind))
        if outfile is None: return
        outfile.write(self.shownContent)
        outfile.close()

    def step3(self, event=""):
        self.state = "3"
        self.resetState()
        self.shownContent = ""
        self.backArrow(self.step2, "step2")
        self.menuBox(220, 600, self.showHistory, "showHistory")
        self.menuBox(400, 600, lambda e: self.saveFile(e, kind="eligible"), "save")
        self.drawCourse()
    
    def showHistory(self, event=""):
        # here we show the history of the students
        if self.activeCourse:
            # print(self.activeCourse.dir, self.activeCourse.progressFile);input()
            notel, st = checkExams.Enrolled.count(kind = "eligible")
            if st:
                print(notel, st)
                reply = messagebox.askyesno("results", '''Έγινε έλεγχος και διαπιστώθηκε ότι {} από τους {} φοιτητές 
που έχουν εγγραφεί στο μάθημα "{}" για εξέταση ευρίσκονται στο φοιτητολόγιο του μαθήματος, και έχουν δικαίωμα να εξεταστούν. 
θέλετε στην κατάσταση να περιληφθεί το ιστορικό της ως τώρα συμμετοχής τους;'''.format(notel, st, Course.activeCourse.name))
                if reply: self.displayData(kind = "eligible", exams=True)
                else: self.displayData(kind = "eligible", exams=False)
        else:
            self.error( "Προσοχή πρέπει να ορίσετε μάθημα στο βήμα 1")

    # helper
    def round_rectangle(self, x1, y1, x2, y2, radius=30, text = "", **kwargs):
        fSize = 40
        points = [x1+radius, y1, x1+radius, y1, x2-radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
                x2, y1+radius, x2, y2-radius, x2, y2-radius, x2, y2, x2-radius, y2, x2-radius, y2,
                x1+radius, y2, x1+radius, y2, x1, y2, x1, y2-radius, x1, y2-radius, x1, y1+radius,
                x1, y1+radius, x1, y1]
        middle = x1 + (x2-x1)//2, y1 + (y2-y1)//2
        
        self.renderItems.append(self.canvas.create_polygon(points, **kwargs, smooth=True))
        if text:
            if "tags" in kwargs: txtKwargs = {'tags': kwargs["tags"]} #tag both text and rectangle
            self.renderItems.append(self.canvas.create_text(*middle, text= text, font= ("Calibri", fSize), anchor= 'c', \
            fill=self.borderColor, **txtKwargs ))


class Course:
    theCourses = []
    activeCourse = None
    @staticmethod
    def loadCourses(setCourse=False):
        if os.path.isfile('mycourses.json'):
            try:
                with open('mycourses.json') as jsonFile:
                    theCourses = json.load(jsonFile)
                    print(theCourses)
                    for course in theCourses:
                        Course(**course)
            except: 
                pass 
        if setCourse:
            name  = simpledialog.askstring("ONOMA", \
'''ΟΡΙΣΜΟΣ Ή ΑΛΛΑΓΗ ΤΟΥ ΜΑΘΗΜΑΤΟΣ ΕΞΕΤΑΣΗΣ ...
Δώστε το Όνομα του Μαθήματος που θα εξεταστεί (πχ. Μαθηματικά),
στη συνέχεια θα σάς ζητηθεί να δείξετε τον φάκελο που έχετε αποθηκεύσει  
τα αρχεία βαθμολογιών, και τέλος στον φάκελο αυτό να δείξετε ποιο είναι
το αρχείο που περιέχει τις δηλώσεις της τρέχουσας εξέτασης.
Αν κάποιο από τα στοιχεία αυτά δεν οριστεί δεν μπορείτε να ορίσετε το
μάθημα της εξέτασης...
Αρχίζουμε με το όνομα του μαθήματος''')
            if name: 
                messagebox.showinfo("Επόμενο Βήμα:", '''Τώρα θα σάς ζητηθεί να εντοπίσετε τον 
φάκελο που έχετε αποθηκεύσει τα αρχεία 
βαθμολογιών (progress) του μαθήματος "{}" ... '''.format(name) )
                dir = filedialog.askdirectory()
            if name and dir:
                messagebox.showinfo("Επόμενο Βήμα:", '''Τώρα θα σάς ζητηθεί το αρχείο με το βαθμολόγιο της τρέχουσας 
εξεταστικής του μαθήματος "{}" ...'''.format(name) )          
                filename = filedialog.askopenfilename()
            if name and dir and filename:
                Course(name, dir, filename, True)
                messagebox.showinfo("ΟΚ", '''Ορίστηκε πλήρως το μάθημα {}'''.format(name))
                Course.saveCourses()
                return Course.activeCourse
            else:
                messagebox.showerror("error", "Προσοχή το μάθημα δεν ορίστηκε, ξαναπροσπαθήστε", icon="error")
        return Course.activeCourse

    @staticmethod
    def saveCourses():
        theCourses = []
        for c in Course.theCourses:
            if c == Course.activeCourse: activeCourse = 1
            else: activeCourse = 0
            theCourses.append({"name": c.name, "dir": c.dir, "progressFile": c.progressFile, "active":activeCourse})
        with open('mycourses.json', "w") as outJson:
            json.dump(theCourses, outJson, ensure_ascii=False)
    
    def __init__(self, name, dir, progressFile, active):
        self.name = name
        self.dir = dir
        self.progressFile = progressFile
        self.active = active
        Course.theCourses.append(self)
        if self.active: Course.activeCourse = self

def main():
    window = MyApp()
    window.mainloop()

if __name__ == "__main__":
    main()

