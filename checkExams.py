# NMA June 2020 v.01
import os
import re
import xlrd

# TODO : get dir of files
DEBUG = False

# auxiliary to upper Greek
def greek_to_upper(w):
    '''an auxiliary function to put a word in capitals and eliminate accented characters'''
    gr_up = {'Ύ':'Υ', 'Έ':'Ε', 'Ά':'Α', 'Ό':'Ο', 'Ί':'Ι', 'Ή':'Η', 'Ώ':'Ω'}
    w_up = w.upper().strip()
    for x in gr_up:
        w_up = w_up.replace(x, gr_up[x])
    return w_up

class Enrolled:
    ''' class of enrolled students '''
    students = {}
    courseDir = None # the dir of historic grades
    examFile = None # the exams enrollment file
    progressFile = None # the progress course enrollment file

    @staticmethod
    def emailsNotEligible():
        if not Enrolled.students: return ""
        emails = ""
        for s,S in Enrolled.students.items():
            if not S.eligibility : emails += S.email +"; "
        return emails.strip("; ")

    @staticmethod
    def showStudents(kind="not eligible", exams=False):
        if not Enrolled.students: return ""
        examsText = "/ και η συμμετοχή τους" if exams else ""
        if kind == "not eligible":
            toShow = "  ΦΟΙΤΗΤΕΣ ΧΩΡΙΣ ΔΙΚΑΙΩΜΑ ΣΥΜΜΕΤΟΧΗΣ\n\n"
        elif kind == "eligible":
            toShow = "  ΦΟΙΤΗΤΕΣ ΜΕ ΔΙΚΑΙΩΜΑ ΣΥΜΜΕΤΟΧΗΣ\n\n"
        else: return ""
        toShow += " {:}\t{:}\n\n".format("ΕΠΩΝΥΜΟ, ΟΝΟΜΑ", "AM, email"+examsText)
        for s,S in sorted(Enrolled.students.items(), key= lambda x : x[1].name):
            if (kind == "not eligible" and not S.eligibility ) or (kind == "eligible" and S.eligibility):
                toShow += " {:}\t{:}\t{}\n".format(S.name, S.am, S.email)
                if exams:
                    for exam in S.exams:
                        toShow += "\t"+":\t\t".join(list(exam))+"\n"
        toShow += "\n\n Συνολικά {} φοιτητές από {} που έχουν εγγραφεί στην εξέταση.".format(*Enrolled.count(kind)) 
        if DEBUG: print("toshow=", toShow); input()
        return toShow

    @staticmethod
    def count(kind = "not eligible"):
        if Enrolled.students:
            count = 0
            for s,S in Enrolled.students.items():
                if kind == "not eligible" and not S.eligibility: count += 1
                elif kind == "eligible" and S.eligibility: count += 1
            return count, len(Enrolled.students) 
        else: False, False

    @staticmethod
    def findAmInFiles(name):
        for f in os.listdir(Enrolled.courseDir):
            if f.endswith('xlsx') and not f.startswith(".") and not f.startswith("~"):
                # print(f, end = ", ")
                fname = os.path.join(Enrolled.courseDir, f)
                # workbook = xlrd.open_workbook(fname)
                workbook = xlrd.open_workbook(fname, on_demand = True)
                worksheet = workbook.sheet_by_index(0)
                first_row = [] # The row where we stock the name of the column
                for col in range(worksheet.ncols):
                    first_row.append( worksheet.cell_value(0,col) )
                # transform the workbook to a list of dictionnary
                for row in range(1, worksheet.nrows):
                    elm = {}
                    for col in range(worksheet.ncols):
                        if first_row[col] in ['AM', 'Παλαιός ΑΜ', 'Επώνυμο, Όνομα', 'Βαθμός']:
                            elm[first_row[col]]=worksheet.cell_value(row,col)
                    if elm['Επώνυμο, Όνομα'] == name.strip(): 
                        # print(elm)
                        return elm['AM']
        return False

    @staticmethod
    def load(dir, progressFile):
        if DEBUG: 
            print("entering load....................", dir, progressFile); input()
            print(dir, progressFile)
        
        #auxiliary function to find the AM of enrolled student
        def findAM(line):
            # for testing purposes...
            name = greek_to_upper(", ".join(line[:2]))
            # print(name)
            am = Enrolled.findAmInFiles(name)
            # print("am =", am);input()
            if am: return am
            if len(line) < 5: return False # eclass records should have at least 5 fields
            if "@upnet" in line[2]: 
                am = re.findall("up([0-9]+?)@", line[2]) 
                if am: return am[0]
                name = greek_to_upper(", ".join(line[:2]))
                # print(name); input()
                am = re.findall("ece([0-9]+?)@", line[2]) #ECE
                if am: return "22"+am[0]
                am = re.findall("ceid([0-9]+?)@", line[2]) #CEID
                if am: return "23"+am[0]
            # other email accounts
            if line[3].startswith("up"): am = line[3].strip("up")
            elif line[4].startswith("up"): am = line[4].strip("up")
            if am: return am
            if len(line[3])==7 and line[3].isdigit(): return line[3]
            if len(line[3]) == 5 and line[4].isdigit(): return line[3]
            # if not found so far, search by name in historic files
            return False

        # check existance of dir, progressFile, examFile
        try:
            files = os.listdir(dir)
        except: 
            print('the dir given does not exist in file system')
            return False
        if not files: 
            print('no files in given dir')
            return False
        else:
            Enrolled.courseDir = dir
        if os.path.isfile(progressFile):
            Enrolled.progressFile = progressFile
        else:
            print('progressFile not found')
            return False
        
        f = [x for x in files if "_users" in x and not x.startswith(".")]
        if len(f)==1: 
            fname = f[0]
            Enrolled.examFile = os.path.join(dir, fname)
        else:
            print('examFile not found')
            return False # the exams file is missing ...
        
        # print("\n".join([Enrolled.progressFile, Enrolled.examFile, Enrolled.courseDir]));input()
        
        # load enrolled students
        for line in open(Enrolled.examFile, "r", encoding="utf-8"):
            if "@" in line:
                line = line.split("\t")
                name = line[0]
                surname = line[1]
                if not "@upatras" in line[2]: email = line[2] # students do not have @upatras email
                am = findAM(line)
                if am : Enrolled(greek_to_upper(", ".join(line[:2])), am, email)
        # for st in Enrolled.students: print(Enrolled.students[st])
        # input()

        # load their grades history if there are historic grades available (optional) and check eligibility
        Enrolled.loadHistoricGrades(dir)
        return True # successful loading


    @staticmethod
    def loadHistoricGrades(dir):
        theProgressFile = os.path.split(Enrolled.progressFile)[1]
        if DEBUG: 
            print("entering loadHistoricGrades.....", theProgressFile); input()
            print("... γίνεται έλεγχος στα αρχεία: ", end = "")
        for f in os.listdir(dir):
            if f.endswith('xlsx') and not f.startswith(".") and not f.startswith("~"):
                print(f, end = ", ")
                fname = os.path.join(dir, f)
                exam = f.strip(".xlsx")
                workbook = xlrd.open_workbook(fname)
                workbook = xlrd.open_workbook(fname, on_demand = True)
                worksheet = workbook.sheet_by_index(0)
                first_row = [] # The row where we stock the name of the column
                for col in range(worksheet.ncols):
                    first_row.append( worksheet.cell_value(0,col) )
                # transform the workbook to a list of dictionnary
                for row in range(1, worksheet.nrows):
                    elm = {}
                    for col in range(worksheet.ncols):
                        #{'AA': 1.0, 'AM': '1004086', 'Παλαιός ΑΜ': '227927', 'Επώνυμο, Όνομα': 'ΣΤΟΥΜΠΟΣ, ΧΡΙΣΤΟΣ ΝΙΚΟΛΑΟΣ', 'Πατρώνυμο': 'ΝΙΚΟΛΑΟΣ', 'Εξάμ': '14', 'Βαθμός': 'NS', 'Πρόγραμμα (Περιγραφή)': 'Προπτυχιακό Πρόγραμμα Σπουδών THMTY', 'Χρήστης': 'AVOURIS', 'Ημερομηνία': 43293.0, 'Αριθμός Βαθμολογίου': '29498'}
                        if first_row[col] in ['AM', 'Παλαιός ΑΜ', 'Επώνυμο, Όνομα', 'Βαθμός']:
                            elm[first_row[col]]=worksheet.cell_value(row,col)
                    if DEBUG: print(elm)
                    if elm['AM'].strip() in Enrolled.students.keys():
                        myAM = elm['AM'].strip()
                    elif elm['Παλαιός ΑΜ'].strip() in Enrolled.students.keys():
                        myAM = elm['Παλαιός ΑΜ'].strip() 
                    else: myAM = False
                    if myAM:
                        # print(myAM, f, theProgressFile, f==theProgressFile)
                        if f == theProgressFile:
                            Enrolled.students[str(myAM)].eligibility = True
                        else:
                            Enrolled.students[str(myAM)].exams.append((exam, elm['Βαθμός']))  

    def __init__(self, name, am, email="", ):
        self.name = name
        self.am = am.strip()
        self.email = email.strip()
        self.exams = []
        self.eligibility = None
        Enrolled.students[am] = self
    def __repr__(self):
        elig = "ok" if self.eligibility else "NO"
        out = " - ".join([self.name, self.am, self.email, elig])+"\n"
        for exam in self.exams:
            out += "\t"+":\t\t".join(list(exam))+"\n"
        return out

if __name__ == "__main__":
    # TODO find the file of this exam
    dir = input("Δώστε τον φάκελο των ιστορικών αρχείων")
    # dir = "/Users/nma/Desktop/Grading-history/Ιστορικό βαθμολόγησης/Εισαγωγή στους Υπολογιστές"
    dir = r"C:\Users\Administrator\Desktop\web"
    thisExamFileName = input("Δώστε το όνομα του αρχείου progress της εξέτασης")
    # thisExamFileName = "/Users/nma/Desktop/Grading-history/Ιστορικό βαθμολόγησης/Εισαγωγή στους Υπολογιστές/ECE_Υ103_Ιουν. 2020.xlsx"
    thisExamFileName = r"C:\Users\Administrator\Desktop\web\export_20200618015318.xlsx" 
    
    Enrolled.load(dir, thisExamFileName)
    if DEBUG: 
        print("\n\n List of enrolled students .... ")
        for st in Enrolled.students: print(Enrolled.students[st])


    print('\n\nNOT ELIGIBLE FOR THIS EXAM')
    print(Enrolled.showStudents(exams=True))

    # count = 0
    # for st, S in Enrolled.students.items(): 
    #     if not S.eligibility: print(S);count += 1
    # print("Σύνολο =", count)

    print('\n\nELIGIBLE FOR THIS EXAM')
    print(Enrolled.showStudents(kind="eligible", exams=True))
    # count = 0
    # for st, S in Enrolled.students.items(): 
    #     if S.eligibility: print(S);count += 1

    print("Σύνολο =", Enrolled.count())

    

    # TODO send email ...

    email = '''\nΑγαπητοί φοιτητές,
    μετά από έλεγχο που έγινε διαπιστώσαμε ότι δεν έχετε δικαίωμα 
    να συμμετάσχετε στην εξέταση του μαθήματος, κατά συνέπεια θα διαγραφείτε 
    από την εξέταση του μαθήματος στην πλατφόρμα exams.eclass.upatras.gr
    Αν η διαγραφή αυτή γίνεται από λάθος στον έλεγχο, παρακαλούμε όπως
    έλθετε σε άμεση επαφή μαζί μας.
    Οι διδάσκοντες'''
    print(50*"=")
    print("\n\n email φοιτητών που είναι εγγεγραμμένοι που δεν έχουν δικαίωμα να συμμετάσχουν στην εξέταση .... ")
    for s, S in Enrolled.students.items(): 
        if not S.eligibility: print(S.email, end="; ")

