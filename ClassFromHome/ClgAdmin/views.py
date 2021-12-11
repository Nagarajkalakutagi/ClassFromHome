import json
import os
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import JsonResponse
import pandas as pd

from .forms import ModelStudentForm, ModelFacultyOwn, ExtraFacultyForm
from .models import Admin_extend, TempFileField, VideoUpload, Fac_notes, Assignment_activity, Student_activity, \
    Assignment_submit
from django.contrib.auth import login
from django.shortcuts import render, HttpResponse, redirect,HttpResponseRedirect
from . import forms
from .models import StudentModel,FacultyModel,Admin_activity,Semester,Faculty_activity
from .backend import MyStudentAuthBackend,MyFacultyAuthBackend
# Create your views here.
from django.db import connection
from django.contrib.auth import authenticate
from django.contrib import messages, auth
from django.contrib.sessions.models import Session
from django.core.management import call_command
from password_generator import PasswordGenerator
from django.forms.models import ValidationError
otp=0
gmail=""
admin_data={}
temp=""
def index(request):
    return render(request,'ClgAdmin/index.html')
def adminloginpage(request):
    if request.method=="POST":
        logform=forms.LoginForm(request.POST)
        if logform.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                auth.login(request,user=user,backend='django.contrib.auth.backends.ModelBackend')
                request.session['is_admin_logged'] = True
                return redirect('admin_home')
            else:
                messages.info(request, 'Invalid Username or Password',extra_tags='adminlog')
                return redirect('admin-login')
    else:
        logform = forms.LoginForm()
        global temp
        temp = 'adminloginpage'
        return render(request,'ClgAdmin/adminloginpage.html',{'logform':logform})

def adminlogout(request):
    del request.session['is_admin_logged']
    auth.logout(request)
    return redirect('admin-login')

def facultyloginpage(request):
    if request.method=="POST":
        logform = forms.FacultyLogform(request.POST)
        if logform.is_valid():
            back = MyFacultyAuthBackend()
            fac_user=back.authenticate(email=logform.cleaned_data['fac_gmail'],password=logform.cleaned_data['fac_password'])
            if fac_user is not None:
                auth.login(request,user=fac_user,backend='ClgAdmin.backend.MyFacultyAuthBackend')
                print("The faculty user",request.user.id)
                request.session['is_faculty_logged']=True
                return redirect('faculty_dashboard')
            else:
                messages.error(request, 'Invalid Username or Password ',extra_tags='faclog')
                return redirect('faculty-login')
    else:
        logform = forms.FacultyLogform()
        global temp
        temp = 'facultyloginpage'
        return render(request,'ClgAdmin/facultyloginpage.html',{'logform':logform})

def student_dashboard(request):
    print(request)
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        print(request.user.id)
        stud=StudentModel.objects.get(id=request.user.id)
        cur11=connection.cursor()
        cur11.execute("select st.stud_firstname||' '||st.stud_lastname as fullname,sm.sem_name,st.stud_gmail,st.stud_phone from clgadmin_studentmodel st,clgadmin_admin_activity ac,clgadmin_semester sm where st.admin_ac_id_id=ac.admin_ac_id and ac.sem_id_id=sm.sem_id and st.id="+str(request.user.id))
        stud=cur11.fetchall()

        cur14=connection.cursor()
        cur14.execute("select acx.clg_name from clgadmin_studentmodel st,clgadmin_admin_activity ac,clgadmin_admin_extend acx  where st.admin_ac_id_id=ac.admin_ac_id and ac.admin_id_id=acx.admin_id_id  and st.id="+str(request.user.id))
        clg_name=cur14.fetchall()


        print(stud)
        cur10=connection.cursor()
        cur10.execute("select st.id,vi.vid_id,vi.vid_path,vi.vid_text,vi.vid_up_date,fc.subject,f.fac_firstname||' '||f.fac_lastname as fullname from clgadmin_studentmodel st,clgadmin_faculty_activity fc,clgadmin_facultymodel f,clgadmin_videoupload vi where st.admin_ac_id_id=fc.admin_ac_id_id and vi.fac_ac_id_id=fc.fac_ac_id and fc.fac_id_id=f.id and st.id="+str(request.user.id)+" order by -vi.vid_up_date;")
        stud_video=cur10.fetchall()
        print(stud_video)

        cur11=connection.cursor()
        cur11.execute("select st.id,nt.note_file_path,nt.note_text,nt.note_up_date,fc.subject ,f.fac_firstname||' '||f.fac_lastname as fullname from clgadmin_studentmodel st,clgadmin_faculty_activity fc,clgadmin_facultymodel f,clgadmin_fac_notes nt where st.admin_ac_id_id=fc.admin_ac_id_id and  nt.fac_ac_id_id=fc.fac_ac_id and fc.fac_id_id=f.id and  st.id="+str(request.user.id)+" order by -nt.note_up_date;")
        stud_notes=cur11.fetchall()
        print(stud_notes)

        cur12 = connection.cursor()
        cur12.execute("select st.id,a.assign_file_path,a.assign_ac_text,a.assign_up_date,fc.subject ,f.fac_firstname||' '||f.fac_lastname as fullname ,a.assign_ac_id ,a.fac_ac_id_id from clgadmin_studentmodel st,clgadmin_faculty_activity fc,clgadmin_facultymodel f,clgadmin_Assignment_activity a where st.admin_ac_id_id=fc.admin_ac_id_id and  a.fac_ac_id_id=fc.fac_ac_id and fc.fac_id_id=f.id and  st.id=" + str(request.user.id) + " order by -a.assign_up_date;")
        assign_notes = cur12.fetchall()
        print("Notes for student")

        list_asign_notes=[list(d) for d in assign_notes]
        cur13=connection.cursor()
        cur13.execute("select assign_ac_id_id,assign_file_path, assign_accept,assign_reject,assign_comment from clgadmin_assignment_submit where stud_id_id="+str(request.user.id))
        print("submit daa")
        assign_sub=cur13.fetchall()
        for x in list_asign_notes:
            for y in assign_sub:
                if y[0] is x[6]:
                    x.append(True)
                    x.append(y[1])
                    x.append(y[2])
                    x.append(y[3])
                    x.append(y[4])
        print("checked values")
        print(list_asign_notes)


        return render(request,'ClgAdmin/student_dashboard.html',{ 'clg_name':clg_name,'stud':stud,'stud_video':stud_video,'stud_notes':stud_notes,'assign_notes':list_asign_notes})
    else:
        return redirect('student-login')

def studentloginpage(request):
    if request.method=='POST':
        print(request.POST)
        logform = forms.StudentLogform(request.POST)
        print(logform.is_valid())
        if logform.is_valid():
            back=MyStudentAuthBackend()
            usrobj=back.authenticate(email=logform.cleaned_data['stud_gmail'],password=logform.cleaned_data['stud_password'])
            print(usrobj)
            if usrobj is not None:
                auth.login(request=request,user=usrobj,backend='ClgAdmin.backend.MyStudentAuthBackend')
                print(request.user.is_authenticated)
                request.session['is_stud_logged']=True
                return redirect('student_dashboard')
            else:
                messages.error(request, 'Invalid Username or Password ',extra_tags='studlog')
                return redirect('student-login')
        else:
            print("Form is not a valid")
    else:
        logform = forms.StudentLogform()
        global temp
        temp = 'studentloginpage'
        return render(request,'ClgAdmin/studentloginpage.html',{'logform':logform})

def studentlogout(request):
    del request.session['is_stud_logged']
    auth.logout(request)
    return redirect('student-login')

def adminregpage(request):
    global admin_data
    if request.method=='POST':
        adminregform = forms.AdminRegForm(request.POST)
        if adminregform.is_valid():
            if adminregform.clean_clg_phone():
                admin_name=adminregform.cleaned_data['admin_name']
                admin_gmail=adminregform.cleaned_data['admin_gmail']
                admin_clg_name=adminregform.cleaned_data['admin_clg_name']

                if User.objects.filter(username=admin_name).exists():
                    print("Username is already taken ")
                    messages.error(request, 'Username is already taken',extra_tags="ad-reg")
                    return redirect('admin-reg')
                elif "gmail.com" not in admin_gmail:
                    print("invalid domain of gmail ")
                    messages.error(request,'invalid domain of gmail',extra_tags='ad-reg')
                    return redirect('admin-reg')
                elif User.objects.filter(email=admin_gmail):
                    print("Email is already taken")
                    messages.error(request, 'Email is already taken',extra_tags='ad-reg')
                    return redirect('admin-reg')
                else:
                    print(adminregform.cleaned_data['admin_gmail'])
                    admin_data = {'admin_firstname': adminregform.cleaned_data['admin_firstname'],
                                  'admin_lastname': adminregform.cleaned_data['admin_lastname'],
                                  'admin_username': adminregform.cleaned_data['admin_name'],
                                  'admin_gmail': adminregform.cleaned_data['admin_gmail'],
                                  'admin_clg_name': adminregform.cleaned_data['admin_clg_name'],
                                  'admin_clg_phone': adminregform.cleaned_data['admin_clg_phone']
                                  }
                    global nt
                    global page
                    global gmail
                    page = 'admin-reg'
                    gmail = adminregform.cleaned_data['admin_gmail']
                    return resendOtp(request)
            else:
                messages.error(request, "Invalid phone number",extra_tags='ad-reg')
                return redirect('admin-reg')
        else:

            return render(request,'ClgAdmin/adminregpage.html',{'adminregform':adminregform})
    else:
        adminregform = forms.AdminRegForm()
        global temp
        temp = ''
        return render(request,'ClgAdmin/adminregpage.html',{'adminregform':adminregform})

def otpsubmit(request):
    global admin_data
    global page
    global gmail
    adgmail=gmail
    print(admin_data)
    cotp = request.POST['otp']
    global otp
    print(otp)
    sotp = str(otp)
    if sotp == cotp and adgmail==gmail:
        otp = ""
        print("otp is matched")
        setpasswordform=forms.PasswordForm()
        return render(request,'ClgAdmin/setadminpassword.html',{'setpasswordform':setpasswordform})
    else:
        messages.info(request, 'OTP is Not Matched',extra_tags='otpsubmit')
        return render(request,'ClgAdmin/enterotp.html')

def setpassword(request):
    global page
    global gmail
    global temp
    global admin_data
    if request.method == 'POST':
        print(request.POST)
        setpasswordform = forms.PasswordForm(request.POST)
        if setpasswordform.is_valid():
            password1=setpasswordform.cleaned_data['password1']
            password2 = setpasswordform.cleaned_data['password2']
            if password1==password2:
                if temp == "adminloginpage":
                    nn = User.objects.get(email=gmail)
                    print('*************************')
                    print(nn)
                    nn.set_password(password2)
                    nn.save()
                    return redirect("admin-login")

                elif temp == "studentloginpage":
                    nn = StudentModel.objects.get(stud_gmail=gmail)
                    nn.set_password(password2)
                    nn.save()
                    return redirect('student-login')

                elif temp == "facultyloginpage":
                    nn = FacultyModel.objects.get(fac_gmail=gmail)
                    nn.set_password(password2)
                    nn.save()
                    return redirect('faculty-login')

                else:
                    try:
                        username=admin_data['admin_username']
                    except Exception as e:
                        print(e)
                    admin_data['admin_password']=password2
                    admin_reguser = User.objects.create_user(username=username,
                                                   email=admin_data['admin_gmail'],
                                                   password=password2,
                                                   first_name=admin_data['admin_firstname'],
                                                   last_name=admin_data['admin_lastname']
                                                   )
                    admin_reguser.save()
                    regobj = Admin_extend(admin_id=admin_reguser,admin_phone=admin_data['admin_clg_phone'],clg_name=admin_data['admin_clg_name'])
                    regobj.save()
                return render(request,'ClgAdmin/adminregsucces.html')
            else:
                print("password couldn't match")
                messages.error(request,"password couldn't match",extra_tags='set-password')
                return redirect('setpassword')
        else:
            return HttpResponse('form is not valid ')
    else:
        print(request.method)
        setpasswordform = forms.PasswordForm()
        return render(request,'ClgAdmin/setadminpassword.html',{'setpasswordform':setpasswordform})

import math, random


def admin_home(request):
    if request.session.has_key('is_admin_logged'):
        if request.user.is_authenticated:
            courseform=forms.AddCourseForm()
            cur1=connection.cursor()
            cur1.execute("select count(st.stud_id),ac.admin_ac_id,sm.sem_name,ac.course from clgadmin_admin_activity ac,clgadmin_Semester sm,clgadmin_Studentmodel st where ac.sem_id_id=sm.sem_id and st.admin_ac_id_id=ac.admin_ac_id and ac.admin_id_id="+str(request.user.id))
            course_data=cur1.fetchall()
            cur6=connection.cursor()
            cur6.execute("select a.first_name||''||a.last_name as fullname,a.email,ax.clg_name,ax.admin_phone from clgadmin_admin_extend ax,auth_user a where ax.admin_id_id=a.id and a.id="+str(request.user.id))
            global admin_data
            admin_data=cur6.fetchall()

            cur5 = connection.cursor()
            cur5.execute("select fc.fac_id_id,fc.fac_ac_id,fc.subject,fc.admin_ac_id_id,f.fac_gmail,f.fac_firstname||''||f.fac_lastname as fullname,f.fac_phone from clgadmin_faculty_activity fc,clgadmin_facultymodel f where fc.fac_id_id=f.id and fc.admin_ac_id_id=" + str(request.user.id))
            fac_sub_data = cur5.fetchall()
            admin=User.objects.get(id=request.user.id)

            fac_own=FacultyModel.objects.filter(admin_id=admin)
            print("Faculty details")
            print(fac_own)
            extra_fac=ExtraFacultyForm()
            return render(request,'ClgAdmin/admin_home.html',{'extra_fac':extra_fac,'fac_own':fac_own,'courseform':courseform,'course_data':course_data,'admin_data':admin_data,'fac_sub_data':fac_sub_data})
        else:
            return HttpResponse('done')
    else:
        return redirect('admin-login')

def getfacown(request):
    if request.is_ajax():
        print(request.GET)
        admin=User.objects.get(username=request.GET['admin_id'])
        facd=FacultyModel.objects.get(Q(id=request.GET['fac_id']) & Q(admin_id=admin.id))
        print(facd)
        dict={
            'id':facd.id,
            'fac_gmail':facd.fac_gmail,
            'fac_firstname':facd.fac_firstname,
            'fac_lastname':facd.fac_lastname,
            'fac_phone':facd.fac_phone
        }
        fac_own_form=ModelFacultyOwn(dict)

        return HttpResponse(fac_own_form)
def facupdateown(request):
    print(request.POST)

    facd = FacultyModel.objects.get(Q(fac_gmail=request.POST['fac_gmail']) & Q(admin_id=request.user.id))
    dict={
        'fac_gmail':request.POST['fac_gmail'],
        'fac_firstname':request.POST['fac_firstname'],
        'fac_lastname':request.POST['fac_lastname'],
        'fac_phone':request.POST['fac_phone']
    }

    fac_own_form = ModelFacultyOwn(dict,instance=facd)
    if fac_own_form.is_valid():
        fac_own_form.save()
        print("Form updated successfully valid")
        messages.success(request,'updated successfully ',extra_tags='fac_up')
        return redirect('admin_home')

    else:
        print(fac_own_form)
        messages.success(request, 'Error ',extra_tags='fac_error')
        return redirect('admin_home')


def getstdata(request):
    stud_id=request.GET['stud_id']
    admin_ac_id=request.GET['admin_ac_id']
    #st=StudentModel.objects.get(Q(stud_id=stud_id) & Q(admin_ac_id=admin_ac_id))
    #print("Dajdlfkjdsf")
    #print(st)
    cur3=connection.cursor()
    q="select stud_id,stud_firstname,stud_lastname,stud_gmail,stud_phone from clgadmin_studentmodel where admin_ac_id_id={0} and stud_id='{1}'".format(admin_ac_id,stud_id)
    cur3.execute(q)
    st=cur3.fetchall()
    #cur3.execute('select stud_id,stud_firstname,stud_lastname,stud_gmail,stud_phone from clgadmin_studentmodel where admin_ac_id_id='+str(admin_ac_id)+'and stud_id=')
    #data=cur3.fetchall()
    #print(data)
    data_dict={
        'stud_id':st[0][0],
        'stud_gmail':st[0][3],
        'stud_firstname':st[0][1],
        'stud_lastname':st[0][2],
        'stud_phone':st[0][4]
    }
    modelform=ModelStudentForm(data_dict)

    return HttpResponse(modelform)

def editstudentsubmit(request):
    print(request.POST)
    data_dict = {
        'stud_id': request.POST['stud_id'],
        'stud_gmail':request.POST['stud_gmail'],
        'stud_firstname': request.POST['stud_firstname'],
        'stud_lastname': request.POST['stud_lastname'],
        'stud_phone': request.POST['stud_phone']
    }
    st = StudentModel.objects.get(Q(stud_id=request.POST['stud_id']) & Q(admin_ac_id=request.POST['admin_ac_id']))

    modelform = forms.ModelFormStudent(data_dict,instance=st)
    print(modelform.is_valid())

    if modelform.is_valid():
        modelform.save()
        return HttpResponse('done')
    else:
        return HttpResponse(modelform.errors)

def adstdashboard(request,ad_ac_id):
    admin = Admin_extend.objects.get(admin_id=request.user)
    cur2=connection.cursor()
    cur2.execute("select ac.course,st.sem_name,s.stud_id,s.stud_firstname,s.stud_lastname,s.stud_gmail,s.stud_phone,s.id,s.admin_ac_id_id from clgadmin_studentmodel s,clgadmin_semester st,"
                 "clgadmin_admin_activity ac where ac.admin_ac_id=s.admin_ac_id_id and st.sem_id=ac.sem_id_id and s.admin_ac_id_id="+str(ad_ac_id))
    st_ad=cur2.fetchall()
    fac=FacultyModel.objects.filter(admin_id=request.user)
    cur5=connection.cursor()
    cur5.execute("select fc.fac_id_id,fc.fac_ac_id,fc.subject,fc.admin_ac_id_id,f.fac_gmail,f.fac_firstname||''||f.fac_lastname as fullname,f.fac_phone from clgadmin_faculty_activity fc,clgadmin_facultymodel f where fc.fac_id_id=f.id and fc.admin_ac_id_id="+str(ad_ac_id))
    fac_sub_data=cur5.fetchall()
    print(fac_sub_data)
    courseform = forms.AddCourseForm()
    studmodel=forms.ModelStudentForm()
    global admin_data
    return render(request,'ClgAdmin/admin_manage.html',{'st_ad':st_ad,'admin':admin,'studmodel':studmodel,"fac_data":fac,'fac_sub_data':fac_sub_data,'courseform':courseform,'admin_data':admin_data})

def asignsub(request):
    print(request.POST['admin_ac_id'])
    print(request.POST)
    admin_ac=Admin_activity.objects.get(admin_ac_id=request.POST['admin_ac_id'])
    fac=FacultyModel.objects.get(Q(id=int(request.POST['fac_id'])) & Q(admin_id=request.user))
    fac_ac=Faculty_activity(admin_ac_id=admin_ac,fac_id=fac,subject=request.POST['fac_subject'])
    fac_ac.save()
    print("assigned subject successfully")
    messages.success(request,"subject assigned successfuly",extra_tags="subjectsuccess")
    return redirect('ad-st-dashboard/'+request.POST['admin_ac_id'])

def addstudent(request):
    print(request.POST)
    stud=forms.ModelStudentForm(request.POST)
    print(stud.is_valid())

    if stud.is_valid():
        st_exist = StudentModel.objects.filter(stud_id=stud.cleaned_data['stud_id']).exists()
        if st_exist:
            print("studnet USN already taken ")
            messages.error(request," studnet USN already taken ",extra_tags="emailerror")
            return redirect('ad-st-dashboard/'+request.POST['admin_ac_id'])


        st_email = StudentModel.objects.filter(stud_gmail=stud.cleaned_data['stud_gmail']).exists()

        if st_email:
            print("studnet Email already taken ")
            messages.error(request, " studnet Email already taken ", extra_tags="emailerror")
            return redirect('ad-st-dashboard/' + request.POST['admin_ac_id'])

        pwo = PasswordGenerator()
        pwo.maxlen = 8
        pwo.minlen = 4
        pwo.excludeschars = "+-{}&_~`[]';:><.()/?,"
        admin_ac_id=Admin_activity.objects.get(admin_ac_id=request.POST['admin_ac_id'])
        password=pwo.generate()
        StudentModel.objects.create_user(admin_ac_id=admin_ac_id,id=stud.cleaned_data['stud_id']
                                            ,firstname=stud.cleaned_data['stud_firstname'],lastname=stud.cleaned_data['stud_lastname'],
                                       email=stud.cleaned_data['stud_gmail'],phone=stud.cleaned_data['stud_phone'],password=password)
        mail_msg="your user id and password is = "+stud.cleaned_data['stud_gmail']+" password= "+password
        try:
            send_mail(
                'Class From Home',
                mail_msg,
                "projectg591307@gmail.com",
                [stud.cleaned_data['stud_gmail']],
                fail_silently=False,
            )
            messages.success(request,"mail cannot be send",extra_tags='emailsuccess')
        except:
            print("mail cannot be send")
            messages.error(request,"mail cannot be send",extra_tags='emailerror')
    return redirect('ad-st-dashboard/' + request.POST['admin_ac_id'])

def deletestudent(request):
    stud_id=request.GET['stud_id']
    admin_ac_id=request.GET['admin_ac_id']
    deldata=StudentModel.objects.get(Q(stud_id=stud_id) & Q(admin_ac_id=admin_ac_id)).delete()
    print(deldata)
    return HttpResponse('done')

def getdelfacacdata(request):
    fac_ac_id=request.GET['fac_ac_id']
    deldata=Faculty_activity.objects.get(fac_ac_id=fac_ac_id).delete()
    print(deldata)
    return HttpResponse('deleted the data')

def admin_addcourse(request):
    if request.method == "POST":
        print(request.POST)
        print(request.FILES)
        courseform = forms.AddCourseForm(request.POST,request.FILES)
        if courseform.is_valid():
            add_file=TempFileField(stud_file=courseform.cleaned_data['stud_file'])
            add_file.save()

           #pandas code starts
            try:
                df = pd.read_excel(add_file.stud_file)  # Reading CSV File
                g = pd.value_counts(df['ID'])  # Counting the number fo repeating data
                a1 = g.max()  # Checking maximum repeating data
                g = pd.value_counts(df['GMAIL'])
                a3 = g.max()
                if a1 == a3:  # Checking all data is present uniquely by comparing the max value
                    c = df['ID'].count()
                    data = []
                    for i in range(c):  # Reading all data one by one
                        s1 = df.loc[i, 'ID']
                        s2 = df.loc[i, 'FIRSTNAME']
                        s3=df.loc[i,'LASTNAME']
                        s4 = df.loc[i, 'GMAIL']
                        s5 = df.loc[i, 'PHONE']
                        nt = (s1, s2, s3,s4,s5)
                        data.append(nt)  # Appending the all tuple in to list
                    for d in data:
                        st_exist = StudentModel.objects.filter(stud_id=d[0]).exists()
                        if st_exist:
                            messages.error(request, 'USN is already taken',extra_tags="pandaserror")
                            return redirect('admin_home')
                        if StudentModel.objects.filter(stud_gmail=d[3]):
                            messages.error(request, 'Gmail is already taken',extra_tags="pandaserror")
                            return redirect('admin_home')

                    sem = Semester.objects.get(sem_name=courseform.cleaned_data['semester'])
                    admin_ac = Admin_activity(admin_id=request.user, course=courseform.cleaned_data['course'],
                                              sem_id=sem)
                    admin_ac.save()
                    print(data)
                    pwo = PasswordGenerator()
                    pwo.maxlen = 8
                    pwo.minlen = 4
                    pwo.excludeschars = "+-{}&_~`[]';:><.()/?,"  # (Optional)
                    for d in data:
                        password = pwo.generate()
                        StudentModel.objects.create_user(admin_ac_id=admin_ac, id=d[0], firstname=d[1], lastname=d[2],
                                                         email=d[3], phone=d[4], password=password)
                        fullname = d[1] + " " + d[2]
                        mail_msg = "Hi " + str(
                            fullname) + " your are successfully Registerd by your College Principle \n And your user_id = " + str(
                            d[0]) + "\nPassword = " + str(password)
                        try:
                            send_mail(
                                'Class From Home',
                                mail_msg,
                                "projectg591307@gmail.com",
                                [d[3]],
                                fail_silently=False,
                            )
                            os.remove(add_file.stud_file)
                        except Exception as e:
                            print(e)
                            messages.info(request, "No  Internet connection")
                    return redirect('admin_home')
                else:
                    print("Data Should be unique")
                    messages.error(request, 'Data should be unique', extra_tags="pandaserror")
                    return redirect('admin_home')
            except Exception as e:
                messages.error(request,"Input Format couldn't match",extra_tags="pandaserror")
                print(e)
                return redirect('admin_home')
        else:
            print(courseform.errors)
            messages.error(request,'Form is not a valid ',extra_tags="pandaserror")
            return redirect('admin_home')
        messages.success(request,'Course added successfully' ,extra_tags="course-add")
        return redirect('admin_home')

def fac_upload(request):
    file=request.FILES['fac_file']
    add_file = TempFileField(fac_file=file)
    add_file.save()
    try:
        df = pd.read_excel(add_file.fac_file)  # Reading CSV File
        g = pd.value_counts(df['ID'])  # Counting the number fo repeating data
        a1 = g.max()  # Checking maximum repeating data
        g = pd.value_counts(df['GMAIL'])
        a3 = g.max()
        if a1 == a3:  # Checking all data is present uniquely by comparing the max value
            c = df['ID'].count()
            data = []
            for i in range(c):  # Reading all data one by one
                s1 = df.loc[i, 'ID']
                s2 = df.loc[i, 'FIRSTNAME']
                s3 = df.loc[i, 'LASTNAME']
                s4 = df.loc[i, 'GMAIL']
                s5 = df.loc[i, 'PHONE']
                nt = (s1, s2, s3, s4, s5)
                data.append(nt)  # Appending the all tuple in to list
            print(data)
            for d in data:
                if FacultyModel.objects.filter(fac_gmail=d[3]):
                    print("Faculty gmail already taken")
                    messages.error(request, 'Gmail is already taken',extra_tags='fac-error')
                    return redirect('admin_home')
            pwo = PasswordGenerator()
            pwo.maxlen = 8
            pwo.minlen = 4
            pwo.excludeschars = "+-{}&_~`[]';:><.()/?,"  # (Optional)

            for d in data:
                password = pwo.generate()
                fac_data = FacultyModel.objects.create_faculy_user(firsntame=d[1], lastname=d[2], email=d[3],
                                                                   phone=d[4], password=password, admin_id=request.user)
                fullname = d[1] + " " + d[2]
                mail_msg = "Hi " + fullname + " your are successfully Registerd by your College Principle as teacher \n And your user_id = " + \
                           str(d[0]) + "\nPassword = " + password
                try:
                    send_mail(
                        'Class From Home',
                        mail_msg,
                        "projectg591307@gmail.com",
                        [d[3]],
                        fail_silently=False,
                    )
                    os.remove(add_file.fac_file)
                except Exception as e:
                    print(e)
                    messages.error(request, "No  Internet connection",extra_tags='fac-error')
            messages.success(request,"Faculty details added",extra_tags='fac_up')
            return redirect('admin_home')
        else:
            print("data should be unique")
            messages.error(request, "data should be unique", extra_tags='fac-error')
            return redirect('admin_home')
    except Exception as e:
        print(e)
        messages.error(request, "Formate couldn't match", extra_tags='fac-error')
        return redirect('admin_home')
    #pandas



def faculty_dashboard(request):
    if request.session.has_key('is_faculty_logged'):
        if request.user.is_authenticated:
            print('This is faculty id',request.user.id)
            fac=FacultyModel.objects.get(id=request.user.id)
            print(fac)
            cur6=connection.cursor()
            cur6.execute("select fc.fac_ac_id,fc.fac_id_id,fc.subject,f.fac_firstname||''||f.fac_lastname as fullname,sm.sem_name from clgadmin_faculty_activity fc,clgadmin_facultymodel f,clgadmin_admin_activity ac,clgadmin_semester sm where fc.fac_id_id=f.id and fc.admin_ac_id_id=ac.admin_ac_id and ac.sem_id_id=sm.sem_id and fc.fac_id_id="+str(request.user.id))
            fac_ac_data=cur6.fetchall()
            print(fac_ac_data)

            cur7=connection.cursor()
            cur7.execute("select f.id,fc.fac_ac_id,vi.vid_path,vi.vid_text,vi.vid_up_date,fc.subject,sm.sem_name from clgadmin_facultymodel f,clgadmin_faculty_activity fc,clgadmin_videoupload vi, clgadmin_admin_activity ac,clgadmin_semester sm where f.id=fc.fac_id_id and fc.fac_ac_id=vi.fac_ac_id_id and fc.admin_ac_id_id=ac.admin_ac_id and ac.sem_id_id=sm.sem_id and f.id="+str(request.user.id)+" order by -vi.vid_up_date")
            vid_data=cur7.fetchall()
            print("videos faclty")
            print(vid_data)

            cur8=connection.cursor()
            cur8.execute("select f.id,fc.fac_ac_id,nt.note_file_path,nt.note_text from clgadmin_facultymodel f,clgadmin_faculty_activity fc,clgadmin_Fac_notes nt where f.id=fc.fac_id_id and fc.fac_ac_id=nt.fac_ac_id_id and f.id="+str(request.user.id))
            note_data=cur8.fetchall()

            cur9 = connection.cursor()
            cur9.execute("select f.id,fc.fac_ac_id,a.assign_file_path,a.assign_ac_text,a.assign_up_date, fc.subject from clgadmin_facultymodel f,clgadmin_faculty_activity fc,clgadmin_Assignment_activity a where f.id=fc.fac_id_id and fc.fac_ac_id=a.fac_ac_id_id and f.id=" + str(request.user.id))
            assign_data = cur9.fetchall()
            cur14=connection.cursor()

            cur14.execute("select  st.stud_firstname||''||st.stud_lastname as fullname,asu.assign_submit_id,asu.assign_file_path,asc.assign_ac_text,asu.assign_up_date,fc.subject ,fc.subject, sm.sem_name ,asu.assign_submit_id,asu.assign_accept,asu.assign_reject,asu.assign_comment from clgadmin_assignment_submit asu,clgadmin_assignment_activity asc,clgadmin_faculty_activity fc,clgadmin_studentmodel st,clgadmin_Admin_activity ac,clgadmin_semester sm  where sm.sem_id=ac.sem_id_id and ac.admin_ac_id=st.admin_ac_id_id and asu.stud_id_id=st.id and asu.assign_ac_id_id=asc.assign_ac_id and asc.fac_ac_id_id=fc.fac_ac_id and fc.fac_id_id="+str(request.user.id)+" order by asu.assign_up_date desc")
            submit_data= cur14.fetchall()
            return render(request,'ClgAdmin/faculty_dashboard.html',{'submit_data':submit_data,'fac':fac,'fac_activity':fac_ac_data,'vid_data':vid_data,'note_data':note_data,'assign_data':assign_data})
    else:
        return redirect('faculty-login')
def facuploadvideo(request):
    print()
    if request.POST:
        fac_ac=Faculty_activity.objects.get(fac_ac_id=request.POST['fac_ac_id'])
        vid_id=VideoUpload(vid_text=request.POST['fac_video_path'],vid_path=request.FILES['fac_video_file'],fac_ac_id=fac_ac)
        vid_id.save()
        messages.info(request,"Video is successfully uploaded")
        return redirect('faculty_dashboard')

def facnotefile(request):
    if request.POST:
        print(request.POST)
        print(request.FILES)
        fac_ac = Faculty_activity.objects.get(fac_ac_id=request.POST['fac_ac_id'])
        note_id=Fac_notes(note_file_path=request.FILES['note-file'],note_text=request.POST['note-title'],fac_ac_id=fac_ac)
        note_id.save()
        return HttpResponse('succesfully done')

def facultylogout(request):
    del request.session['is_faculty_logged']
    auth.logout(request)
    return redirect('faculty-login')


def resendOtp(request):
    digits_in_otp = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    global otp
    global nt
    global page
    global gmail
    otp = ""
    length = len(digits_in_otp)
    for i in range(6):
        otp += digits_in_otp[math.floor(random.random() * length)]
    print(otp)
    try:
        send_mail(
            'One Time Password Varification',
            otp,
            "projectg591307@gmail.com",
            [gmail],
            fail_silently=False,
        )
    except Exception as e:
        print(e)
    print(admin_data)
    return render(request, 'ClgAdmin/enterotp.html')


def forgot(request):
    global nt
    global page
    page = 'forgot'
    global temp
    global gmail
    if request.method == 'POST':
        adminregform = forms.forgot(request.POST)
        back = MyFacultyAuthBackend()
        if adminregform.is_valid():
            print("forgtet page "+temp)
            if temp == "adminloginpage":
                if User.objects.filter(email=adminregform.cleaned_data['admin_gmail']).exists():
                    nt = adminregform.cleaned_data['admin_gmail']
                    print(nt)
                    gmail = nt
                    return resendOtp(request)
                else:
                    print(" thes email is not exist");   messages.error(request,"Account doesn't exit",extra_tags="f-gmail")
                    return redirect('forgot')
            elif temp == "studentloginpage":
                if StudentModel.objects.filter(stud_gmail=adminregform.cleaned_data['admin_gmail']).exists():
                    nt = adminregform.cleaned_data['admin_gmail']
                    print(nt)
                    gmail = nt
                    return resendOtp(request)
                else:
                    print(" thes email is not exist");   messages.error(request,"Account doesn't exit",extra_tags="f-gmail")
                    return redirect('forgot')
            elif temp == "facultyloginpage":
                if FacultyModel.objects.filter(fac_gmail=adminregform.cleaned_data['admin_gmail']).exists():
                    nt = adminregform.cleaned_data['admin_gmail']
                    print(nt)
                    gmail = nt
                    return resendOtp(request)
                else:
                    print(" thes email is not exist");   messages.error(request,"Account doesn't exit",extra_tags="f-gmail")
                    return redirect('forgot')
        else:
            return render(request,'ClgAdmin/forgot.html')
    else:
        adminregform = forms.forgot(request.POST)
        return render(request,'ClgAdmin/forgot.html', {'adminregform':adminregform})



def assignment(request):
    print(request.POST)
    if request.POST:
        print(request.POST)
        fac_ac = Faculty_activity.objects.get(fac_ac_id=request.POST['fac_ac_id'])
        print(fac_ac)
        note_id = Assignment_activity(assign_ac_text=request.POST['asign_title'],fac_ac_id=fac_ac,assign_file_path=request.FILES['asign_file'])
        note_id.save()
    return HttpResponse('succesfully done')

def test(request):
    print(request.POST)
    if request.POST:
        stud=StudentModel.objects.get(id=request.user.id)
        print(stud)
        asign_ac=Assignment_activity.objects.get(assign_ac_id=request.POST['as_ac_id'])
        note_id = Assignment_submit(assign_text=request.POST['note-title'],assign_file_path=request.FILES['note_file'],stud_id=stud,assign_ac_id=asign_ac)
        note_id.save()

    return HttpResponse('succesfully done')

def extrafac(request):
    print(request.POST)
    if request.method=="POST":
        extra_fac=ExtraFacultyForm(request.POST)
        if extra_fac.is_valid():
            fac=FacultyModel.objects.filter(fac_gmail=extra_fac.cleaned_data['fac_gmail']).exists()
            if fac:
                print(fac)
                messages.error(request,'Gmail is already taken ',extra_tags='fac_error')
                return redirect('admin_home')
            else:
                pwo = PasswordGenerator()
                pwo.maxlen = 8
                pwo.minlen = 4
                pwo.excludeschars = "+-{}&_~`[]';:><.()/?,"  # (Optional)
                password = pwo.generate()
                print("password="+password)
                email=extra_fac.cleaned_data['fac_gmail']
                print(email)
                try:
                    send_mail(
                        'Class From Home',
                        password,
                        "projectg591307@gmail.com",
                        [email],
                        fail_silently=False,
                    )
                    fac_create = FacultyModel.objects.create_faculy_user(
                        firsntame=extra_fac.cleaned_data['fac_firstname'],
                        lastname=extra_fac.cleaned_data['fac_lastname'],
                        email=extra_fac.cleaned_data['fac_gmail'],
                        phone=extra_fac.cleaned_data['fac_phone'],
                        admin_id=request.user,
                        password=password
                    )
                    messages.success(request, "Faculty details added successfully", extra_tags='fac_up')
                except Exception as e:
                    print(e)
                    messages.info(request, "No  Internet connection")
            return redirect('admin_home')


    return HttpResponse('done')

def getdelfacown(request):
    if request.is_ajax():
        deldata = FacultyModel.objects.get(Q(id=request.GET['fac_id']) & Q(admin_id=request.user)).delete()
        return HttpResponse('Deleted Successfully')


def accept_status(request):
    print(request.POST)
    if request.method == 'POST':
        sub_id=request.POST.get('ac_st_id',False)
        print("*********************************!!!!!!!")
        print(sub_id)
        ntk = Assignment_submit.objects.filter(assign_submit_id=sub_id).update(assign_accept=True,assign_reject=False,assign_comment=" ")
    return HttpResponse("Assgnament Accepted")

def reject_status(request):
    print(request.POST)
    if request.method == 'POST':
        sub_id = request.POST.get('ac_st_id',False)
        comment = request.POST.get('comment',False)
        print("Assiginament Reject !!!!!!!!!!!!!!!!!!")
        print(sub_id+""+comment)
        nt = Assignment_submit.objects.filter(assign_submit_id=sub_id).update(assign_reject=True,assign_comment=comment,assign_accept=False)
    return HttpResponse("Assgnament Rejected")
