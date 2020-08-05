from http.cookiejar import CookieJar
import bs4
import requests
from java import jclass
import selenium
from selenium import webdriver
class Spider:
    session = requests.session()
    session.cookies=CookieJar()


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'
        ,'Referer':"https://cas.bjtu.edu.cn/auth/login/"
    }


    def __init__(self,loginname,password):
        self.grade=set()
        self.lesson={}
        self.page = self.session.get("https://cas.bjtu.edu.cn/auth/login/", headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36'})
        dic = {}
        lt = bs4.BeautifulSoup(self.page.text, 'html.parser')
        for line in lt.form.findAll('input'):
            if (line.attrs['name'] == 'loginname'):
                break
            dic[line.attrs['name']] = line.attrs['value']
        dic['loginname']=loginname
        dic['password']=password
        self.page=self.session.post("https://cas.bjtu.edu.cn/auth/login/",
                                    data=dic,headers=self.headers)

    def getGrade(self):
        if(self.grade):
            return self.grade
        self._gotoUrl("https://mis.bjtu.edu.cn/module/module/10")
        self._gotoUrl(
            bs4.BeautifulSoup(self.page.text,'html.parser').find(
                id='redirect'
            ).attrs['action']
        )
        self._gotoUrl('https://dean.bjtu.edu.cn/score/scores/stu/view/')


        self.grade=self.grade.union(set(self.get_page_grade(
            self.page
        )))
        for i in range(1,5):
            self._gotoUrl('https://dean.bjtu.edu.cn/score/scores/stu/view/?ctype=ln&page='+str(i))
            self.grade = self.grade.union(set(self.get_page_grade(self.page)))
        return self.grade
    def get_page_grade(self,r):
        grade_selector = bs4.BeautifulSoup(self.page.text, 'html.parser')
        grade_set = []
        for i, grade_item in enumerate(grade_selector.findAll('tr')):
            if (len(grade_item.findAll('td')) != 8):
                continue
            buffer = []
            for j, ch in enumerate(grade_item.findAll('td')):
                if (j == 4):
                    st = ch.text
                    st = st.replace(' ', '').replace('\n', '')
                    buffer.append(st)
                    continue
                elif (j == 2):
                    st = ch.text
                    st = st.split('\n')
                    buffer.append(tuple([y for y in ((st[1] + st[2]).strip().split(' ')) if y != '']))
                    continue
                elif (j == 6 or j == 1 or j==3):
                    buffer.append(ch.text)
                    continue
            grade_set.append(tuple(buffer))
        return grade_set

    def _gotoUrl(self,next_url):
        self.headers['Referer']=self.page.url
        self.page=self.session.get(next_url,headers=self.headers)

    def _Calc_GPA_AVG(self):
        self.getGrade()
        GPA=AVG=total=0
        for grade_item in self.grade:
            if(grade_item[3]=='P' or grade_item[3]=='F'):
                continue
            weight=float(grade_item[2])
            total+=weight
            if(grade_item[3].isdigit()):
                x=float(grade_item[3])
                AVG+=x*weight
                if(x >= 90):
                    GPA+=4.0*weight
                elif(x >= 85):
                    GPA+=3.7*weight
                elif (x >= 81):
                    GPA += 3.3*weight
                elif (x >= 78):
                    GPA += 3.0*weight
                elif (x >= 75):
                    GPA += 2.7*weight
                elif (x >= 72):
                    GPA += 2.3*weight
                elif (x >= 68):
                    GPA += 2.0*weight
                elif (x >= 65):
                    GPA += 1.7*weight
                elif (x >= 63):
                    GPA += 1.3*weight
                elif (x >= 60):
                    GPA += 1.0*weight
            else:
                x=grade_item[3]
                if (x == 'A'):
                    GPA += 4.0*weight
                    AVG += 90*weight
                elif (x == 'A-'):
                    GPA += 3.7*weight
                    AVG += 85*weight
                elif (x == 'B+'):
                    GPA += 3.3*weight
                    AVG += 81*weight
                elif (x == 'B'):
                    GPA += 3.0*weight
                    AVG += 78*weight
                elif (x == 'B-'):
                    GPA += 2.7*weight
                    AVG += 75*weight
                elif (x == 'C+'):
                    GPA += 2.3*weight
                    AVG += 72*weight
                elif (x == 'C'):
                    GPA += 2.0*weight
                    AVG += 68*weight
                elif (x == 'C-'):
                    GPA += 1.7*weight
                    AVG += 65*weight
                elif (x == 'D+'):
                    GPA += 1.3*weight
                    AVG += 63*weight
                elif (x == 'D'):
                    GPA += 1.0*weight
                    AVG +=60*weight
        GPA=round(GPA/total,2)
        AVG=round(AVG/total,2)
        return GPA,AVG

def getgrade(loginname,password):
    # loginname=input("请输入学号")
    # password=input("请输入密码")
    GradeBean=jclass("com.example.studentmagicbox.GradeBean")
    net=Spider(loginname,password)
    result=net._Calc_GPA_AVG()
    jb=GradeBean(result[0],result[1])

    for x in net.getGrade():
        GradeItem=jclass("com.example.studentmagicbox.GradeItem")
        buffer=GradeItem(x[0],x[1][0],x[1][1],x[2],x[3],x[4])
        jb.add_grade(buffer)
    return jb