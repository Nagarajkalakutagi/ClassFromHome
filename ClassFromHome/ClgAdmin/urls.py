from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from . import views
urlpatterns = [
    #home page
    path('',views.index,name='index'),

    #Admin-page
    path('admin-login',views.adminloginpage,name='admin-login'),
    path('admin_home',views.admin_home,name='admin_home'),
    path('admin-addcourse',views.admin_addcourse,name='admin_addcourse'),
    path('setpassword',views.setpassword,name='setpassword'),
    path('admin-reg',views.adminregpage,name='admin-reg'),
    path('otpsubmit',views.otpsubmit,name='otpsubmit'),
    path('resendOtp',views.resendOtp,name='resendOtp'),
    path('forgot',views.forgot,name='forgot'),
    path('admin-logout',views.adminlogout,name='admin-logout'),
    path('fac_upload',views.fac_upload,name='fac_upload'),
    path('ad-st-dashboard/get-st-data',views.getstdata,name='get-st-data'),
    path('edit-student',views.editstudentsubmit,name="edit-student"),
    path('ad-st-dashboard/get-del-st-data',views.deletestudent,name="get-del-st-data"),
    path('addstudent',views.addstudent,name='addstudent'),
    path('ad-st-dashboard/get-del-fac-ac-data',views.getdelfacacdata,name="get-del-fac-ac-data"),
    path('get-fac-own',views.getfacown,name="get-fac-own"),
    path('fac_update_own',views.facupdateown,name='fac_update_own'),
    path('extra_fac',views.extrafac,name="extra_fac"),
    path('get-del-fac-own',views.getdelfacown,name="get-del-fac-own"),

    #Admin-student-details
    path('ad-st-dashboard/<int:ad_ac_id>',views.adstdashboard,name='ad-st-dashboard'),


    #Faculty Page
    path('faculty-login',views.facultyloginpage,name='faculty-login'),
    path('faculty_dashboard',views.faculty_dashboard,name='faculty_dashboard'),
    path('faculty-logout',views.facultylogout,name='faculty-logout'),
    path('asign-sub',views.asignsub,name='asign-sub'),
    path('fac_upload_video',views.facuploadvideo,name='fac_upload_video'),
    path('fac-note-file',views.facnotefile,name="fac-note-file"),

    #Student page
    path('student-login',views.studentloginpage,name='student-login'),
    path('student_dashboard',views.student_dashboard,name='student_dashboard'),
    path('studentlogout',views.studentlogout,name='studentlogout'),

    path('asign_submit',views.test,name='asign_submit'),
    path('assign_upload',views.assignment,name='assign_upload'),
    path('accept_status',views.accept_status,name='accept_status'),
    path('reject_status',views.reject_status,name='reject_status'),


]
if settings.DEBUG:
 urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)