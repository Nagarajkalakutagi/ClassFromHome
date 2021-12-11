import re
from django import forms
from .models import StudentModel, Faculty_activity, FacultyModel


class AdminRegForm(forms.Form):
    admin_firstname = forms.CharField(required=True, max_length=255,
                                 widget=forms.TextInput({'placeholder': 'your first-name','class':'form-control'}))
    admin_lastname = forms.CharField(required=True, max_length=255,
                                 widget=forms.TextInput({'placeholder': 'your last-name','class':'form-control'}))
    admin_name=forms.CharField(required=True,max_length=255,widget=forms.TextInput({'placeholder':'your user-name','class':'form-control'}))
    admin_gmail=forms.EmailField(required=True,max_length=255,widget=forms.EmailInput({'placeholder':'your gmail','class':'form-control'}))
    admin_clg_name = forms.CharField(required=True, max_length=255,widget=forms.TextInput({'placeholder':'your collage name','class':'form-control'}))
    admin_clg_phone = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Phone number','class':'form-control'}))

    def clean_clg_phone(self):
        phone=self.cleaned_data['admin_clg_phone']
        self.bo=re.match("^[6-9]\d{9}$",str(phone))
        if self.bo:
            return self.bo
        else:
            self.bo=False
            return self.bo

class StudentLogform(forms.Form):
    stud_gmail=forms.EmailField(max_length=50,widget=forms.EmailInput(attrs={'placeholder':'Enter your gmail'}))
    stud_password = forms.CharField(max_length=8, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))

class FacultyLogform(forms.Form):
    fac_gmail=forms.EmailField(max_length=50,widget=forms.EmailInput(attrs={'placeholder':'Enter your gmail'}))
    fac_password = forms.CharField(max_length=8, widget=forms.PasswordInput(attrs={'placeholder': 'Enter your password'}))

class LoginForm(forms.Form):
    username=forms.CharField(max_length=40,widget=forms.TextInput(attrs={'placeholder':'Username'}))
    password=forms.CharField(max_length=8,widget=forms.PasswordInput(attrs={'placeholder':'password'}))

class PasswordForm(forms.Form):
    password1=forms.CharField(max_length=8,widget=forms.PasswordInput(attrs={'placeholder':'password','class':'form-control'}))
    password2 = forms.CharField(max_length=8, widget=forms.PasswordInput(attrs={'placeholder': 'confirm password','class':'form-control'}))

class AddCourseForm(forms.Form):
    CH=(('select','select course'),('bca','BCA(Bachelor of Computer Application)'),
        ('b.com','B.com(Bachelor of Commerce'),('bba','BBA'))
    course=forms.CharField(max_length=15,widget=forms.TextInput({'require':'true','placeholder':'Enter Course','class':'form-control'}))
    CH_SEM=(('select','select semester'),('First Semester','First Semester'),('Second Semester','Second Semester')
            ,('Third Semester','Third Semester'),('Fourth Semester','Fourth Semester'),('Fifth Semester','Fifth Semester'),('Sixth Semester','Sixth Semester'))
    semester=forms.ChoiceField(choices=CH_SEM,widget=forms.Select({'require':'true','class':'form-control'}))
    stud_file = forms.FileField(widget=forms.FileInput(attrs={'aria-describedby':'id_stud_file_id','class':'custom-file-input','accept':'.xlsx'}))


class ModelStudentForm(forms.Form):
    stud_id=forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'Enter USN number','require':'true','class':'form-control'}))
    stud_firstname=forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'Enter Firsname ','require':'true','class':'form-control'}))
    stud_lastname=forms.CharField(max_length=50,widget=forms.TextInput({'placeholder':'Enter Lastname','require':'true','class':'form-control'}))
    stud_gmail=forms.EmailField(max_length=90,widget=forms.EmailInput({'placeholder':'Enter Gmail','require':'true','class':'form-control'}))
    stud_phone=forms.CharField(max_length=10,widget=forms.NumberInput({'placeholder':'Enter Phone holder','require':'true','class':'form-control'}))

class ModelFormStudent(forms.ModelForm):
    class Meta:
        model=StudentModel
        fields=['stud_id','stud_firstname','stud_lastname','stud_gmail','stud_phone']

class ModelFormFaculty(forms.ModelForm):
    class Meta:
        model=Faculty_activity
        fields=['subject','fac_ac_id']

class ModelFacultyOwn(forms.ModelForm):
    class Meta:
        model=FacultyModel
        fields=['id','fac_gmail','fac_firstname','fac_lastname','fac_phone']
        widgets={
            'id':forms.HiddenInput()
        }

class ExtraFacultyForm(forms.Form):
    fac_firstname=forms.CharField(max_length=255,required=True,widget=forms.TextInput(attrs={'placeholder':'Enter Firstname','class':'form-control'}))
    fac_lastname = forms.CharField(max_length=255, required=True, widget=forms.TextInput(
        attrs={'placeholder': 'Enter Lastname', 'class': 'form-control'}))
    fac_gmail = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(
        attrs={'placeholder': 'Enter Gmail', 'class': 'form-control'}))
    fac_phone = forms.IntegerField( required=True, widget=forms.NumberInput(
        attrs={'placeholder': 'Enter Phone', 'class': 'form-control'}))



class UploadVideoForm(forms.Form):
    vid_text=forms.CharField(max_length=255,required=True,widget=forms.TextInput({'placeholder':'Enter video title here'}))
    vid_path=forms.FileField(widget=forms.FileInput())

class forgot(forms.Form):
    admin_gmail=forms.EmailField(max_length=50,required=True,widget=forms.EmailInput(attrs={'placeholder':'Enter your gmail','class':'form-control'}))



