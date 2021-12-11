from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class Admin_extend(models.Model):
    admin_id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    clg_name = models.CharField(max_length=255)
    admin_phone = models.CharField(max_length=10)


class Semester(models.Model):
    sem_id = models.AutoField(primary_key=True, unique=True)
    sem_name = models.CharField(max_length=20)


class Admin_activity(models.Model):
    admin_ac_id = models.AutoField(primary_key=True, unique=True)
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE)
    COURSE = [('select', 'Select Course'), ('bca', 'BCA'), ('b.com', 'B.com'), ('bba', 'BBA')]
    course = models.CharField(max_length=10, default='Select Course', choices=COURSE)
    sem_id = models.ForeignKey(Semester, max_length=10, on_delete=models.CASCADE)


class MyFaculyManager(BaseUserManager):
    use_in_migrations = True

    # python manage.py createsuperuser
    def create_faculy_user(self, firsntame, lastname, email, password, phone, admin_id):
        fac_user = self.model(
            fac_firstname=firsntame,
            fac_lastname=lastname,
            fac_phone=phone,
            fac_gmail=email,
            password=password,
            admin_id=admin_id,
        )
        fac_user.set_password(password)
        fac_user.save(using=self._db)
        return fac_user


class FacultyModel(AbstractBaseUser):
    fac_gmail = models.EmailField(max_length=127, unique=True, null=False, blank=False)
    fac_firstname = models.CharField(max_length=50)
    fac_lastname = models.CharField(max_length=50)
    fac_phone = models.CharField(max_length=10, null=True, blank=True)
    admin_id = models.ForeignKey(User, on_delete=models.CASCADE, default=None, null=True)
    is_active = models.BooleanField(default=True)

    objects = MyFaculyManager()

    USERNAME_FIELD = "fac_gmail"
    # REQUIRED_FIELDS must contain all required fields on your User model,
    # but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = ['fac_firstname', 'fac_lastname']

    def __str__(self):
        return self.fac_gmail

    def get_full_name(self):
        return self.fac_gmail

    def get_short_name(self):
        return self.fac_gmail


class Faculty_activity(models.Model):
    fac_ac_id = models.AutoField(primary_key=True, unique=True)
    admin_ac_id = models.ForeignKey(Admin_activity, on_delete=models.CASCADE)
    fac_id = models.ForeignKey(FacultyModel, on_delete=models.CASCADE)
    subject = models.CharField(max_length=40, default=None)


class VideoUpload(models.Model):
    vid_id = models.AutoField(primary_key=True, unique=True)
    vid_text = models.CharField(max_length=255, null=True)
    vid_dur = models.CharField(max_length=10, default=None, null=True)
    vid_up_date = models.DateTimeField(default=now)
    vid_path = models.ImageField(upload_to='Videos')
    fac_ac_id = models.ForeignKey(Faculty_activity, on_delete=models.CASCADE)


class Fac_notes(models.Model):
    note_id = models.AutoField(primary_key=True, unique=True)
    note_text = models.CharField(max_length=255, null=True)
    note_file_path = models.ImageField(upload_to='Notes')
    note_up_date = models.DateTimeField(default=now)
    fac_ac_id = models.ForeignKey(Faculty_activity, on_delete=models.CASCADE, default=None)


class MyStudentManager(BaseUserManager):
    use_in_migrations = True

    # python manage.py createsuperuser
    def create_user(self, admin_ac_id, id, firstname, lastname, phone, email, password):
        stud_user = self.model(
            admin_ac_id=admin_ac_id,
            stud_id=id,
            stud_gmail=email,
            stud_firstname=firstname,
            stud_lastname=lastname,
            stud_phone=phone,
            password=password
        )
        stud_user.set_password(password)
        stud_user.save(using=self._db)
        return stud_user


class StudentModel(AbstractBaseUser):
    stud_id = models.CharField(max_length=10, blank=True)
    stud_gmail = models.EmailField(max_length=127, unique=True, null=False, blank=False)
    stud_firstname = models.CharField(max_length=50)
    stud_lastname = models.CharField(max_length=50)
    stud_phone = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    admin_ac_id = models.ForeignKey(Admin_activity, on_delete=models.CASCADE, default=None, null=True)

    objects = MyStudentManager()

    USERNAME_FIELD = "stud_gmail"
    # REQUIRED_FIELDS must contain all required fields on your User model,
    # but should not contain the USERNAME_FIELD or password as these fields will always be prompted for.
    REQUIRED_FIELDS = ['stud_firstname', 'stud_lastname']

    def __str__(self):
        return self.stud_gmail

    def get_full_name(self):
        return self.stud_gmail

    def get_short_name(self):
        return self.stud_gmail


class Student_activity(models.Model):
    stud_ac_id = models.AutoField(primary_key=True, unique=True)
    stud_id = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    vid_id = models.ForeignKey(VideoUpload, on_delete=models.CASCADE)
    view_st = models.BooleanField(default=False)
    view_time = models.TimeField()


class TempFileField(models.Model):
    fac_file = models.FileField(upload_to='College/Faculty', blank=True, default=None)
    stud_file = models.FileField(upload_to='College/Student', default=None)


class Assignment_activity(models.Model):
    assign_ac_id = models.AutoField(primary_key=True, unique=True)
    assign_ac_text = models.CharField(max_length=255, null=True)
    assign_file_path = models.ImageField(upload_to='Notes')
    assign_up_date = models.DateTimeField(default=now)
    fac_ac_id = models.ForeignKey(Faculty_activity, on_delete=models.CASCADE, default=None)


class Assignment_submit(models.Model):
    assign_submit_id = models.AutoField(primary_key=True, unique=True)
    assign_text = models.CharField(max_length=255, null=True)
    assign_file_path = models.ImageField(upload_to='Notes')
    assign_up_date = models.DateTimeField(default=now)
    stud_id = models.ForeignKey(StudentModel, on_delete=models.CASCADE)
    assign_ac_id = models.ForeignKey(Assignment_activity, on_delete=models.CASCADE)
    assign_accept = models.BooleanField(default=False)
    assign_reject = models.BooleanField(default=False)
    assign_comment = models.CharField(max_length=255, null=True)
