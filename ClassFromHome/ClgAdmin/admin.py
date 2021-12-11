from django.contrib import admin
from . import models
#admin.site.register()

admin.site.register(models.Admin_activity)
admin.site.register(models.Admin_extend)
admin.site.register(models.VideoUpload)
admin.site.register(models.FacultyModel)
admin.site.register(models.Faculty_activity)
admin.site.register(models.StudentModel)
admin.site.register(models.Student_activity)
admin.site.register(models.Semester)