from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
import sqlite3
from joblib import load
from .models import Profile
from django.contrib.auth.models import User
import random
from app1.message_handler import MessageHandler

model=load('./saveModels/model.joblib')

@csrf_exempt

# Create your views here.

def create_table1():
    con=sqlite3.connect('da.db')
    conn=con.cursor()
    conn.execute('CREATE TABLE IF NOT EXISTS details(doctor_name TEXT,doctor_type TEXT,city TEXT,address TEXT,mobile TEXT)')


def add_userdata1(doctor_name,doctor_type,city,address,mobile):
    con=sqlite3.connect('da.db')
    conn=con.cursor()
    conn.execute('INSERT INTO details(doctor_name,doctor_type,city,address,mobile)VALUES(?,?,?,?,?)',(doctor_name,doctor_type,city,address,mobile))
    con.commit()

def display1(doctor_type,city):
    con=sqlite3.connect('da.db')
    conn=con.cursor()
    conn.execute('Select * from details where doctor_type=? and city=?',(doctor_type,city))
    data=conn.fetchall()
    return data







def create_table():
    con=sqlite3.connect('data.db')
    conn=con.cursor()
    conn.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')



def add_userdata(username,password):
    con=sqlite3.connect('data.db')
    conn=con.cursor()
    conn.execute('INSERT INTO userstable(username,password)VALUES(?,?)',(username,password))
    con.commit()


def login_user(username,password):
    con=sqlite3.connect('data.db')
    conn=con.cursor()
    conn.execute('SELECT COUNT(*) FROM userstable WHERE username=? AND password=?',(username,password))
    co=conn.fetchone()
    return co


def display():
    con=sqlite3.connect('data.db')
    conn=con.cursor()
    conn.execute('Select * from userstable')
    data=conn.fetchall()
    return data


    

def HomePage(request):
    return render(request,'home.html',{'navbar':'home'})

def SignupPage(request):
     
      if request.method=="POST":
        if User.objects.filter(username__iexact=request.POST['user_name']).exists():
            return HttpResponse("User already exists")
        create_table()
        add_userdata(request.POST['user_name'],request.POST['password'])
        user=User.objects.create(username=request.POST['user_name'])
        otp=random.randint(1000,9999)
        profile=Profile.objects.create(user=user,phone_number=request.POST['phone_number'],otp=f'{otp}')
        messagehandler=MessageHandler(request.POST['phone_number'],otp).send_otp_via_message()
        red=redirect(f'otp/{profile.uid}/')
        red.set_cookie("can_otp_enter",True,max_age=600)
        return red  
      return render(request, 'sign.html')






def  LoginPage(request):
    if request.method=='POST':
         username=request.POST.get('username')
         password=request.POST.get('password')
         if(len(password)==0 or len(username)==0):
             return HttpResponse('Invalid password or username')
         else:
             count=login_user(username,password)[0]
             if count:
        
                 return redirect('home')
             else:
                 return HttpResponse('Invalid user')
            

    return render(request,'login.html')



def Logout(request):
    return redirect('login')

def predict(request):
    if request.method=='POST':

           gender=int(request.POST.get('gender'))
           yellow_fingers=int(request.POST.get('yellow_fingers'))
           anxiety=int(request.POST.get('anxiety'))
           peer_pressure=int(request.POST.get('peer_pressure'))
        
    
           wheezing=int(request.POST.get('wheezing'))
           alcohol_consuming=int(request.POST.get('alcohol_consuming'))
           coughing=int(request.POST.get('coughing'))
           swallowing_difficulty=int(request.POST.get('swallowing_difficulty'))
           chest_pain=int(request.POST.get('chest_pain'))
           t='M' if(1) else 'F' 
           
           y_predit=model.predict([[alcohol_consuming,chest_pain,swallowing_difficulty,wheezing,coughing,gender,anxiety,peer_pressure,yellow_fingers]])
           if y_predit[0]:
               y_predit='You have been detected postive with Lung Cancer'
           else:
                y_predit='You have been detected negative with Lung Cancer'
           return render(request,'result.html',{'result':y_predit,'yellow_fingers':yellow_fingers,'anxiety':anxiety,'peer_pressure':peer_pressure,
                                               'wheezing':wheezing,'alcohol_consuming':alcohol_consuming,
                                                'coughing':coughing,'swallowing_difficulty':swallowing_difficulty,
                                                 'chest_pain':chest_pain,
                                                 'gender':t
                                                })
                    
               



    return render(request,'predict.html',{'navbar':'predict'})


def finds(request):
    if(request.method=='POST'):
        doctor_name=request.POST.get('name')
        doctor_type=request.POST.get('doctor-type')
        city=request.POST.get('city')
        address=request.POST.get('address')
        mobile_number=request.POST.get('mobile-number')

        create_table1()
        add_userdata1(doctor_name,doctor_type,city,address,mobile_number)
        
        return redirect('finds')

    return render(request,'finds.html')

def search(request):
     if(request.method=='POST'):
        
        doctor_type=request.POST.get('doctor-type')
        city=request.POST.get('city')
        data=display1(doctor_type,city)
        physican=[]
        for i in data:
            t={'name':i[0],'specialty':i[1],'General Physician':i[2],'city':i[3],'address':i[3],'contact_number':i[4]}
            physican.append(t)
        
        return render(request, 'result1.html', {'physicians':physican})
     return render(request,'search.html')







def otpVerify(request,uid):
    if request.method=="POST":
        profile=Profile.objects.get(uid=uid)     
        if request.COOKIES.get('can_otp_enter')!=None:
            if(profile.otp==request.POST['otp']):
                red=redirect("login")
                return red
            return HttpResponse("wrong otp")
        return HttpResponse("10 minutes passed")        
    return render(request,"otp.html",{'id':uid})
