from .models import StudentModel,FacultyModel
import logging


class MyStudentAuthBackend(object):
    def authenticate(self, email, password):
        try:
            stud_user = StudentModel.objects.get(stud_gmail=email)
            print("user ",stud_user)
            if stud_user.check_password(password):
                return stud_user
            else:
                return None
        except Exception as e:
            logging.getLogger("error_logger").error(repr(e))
            return None
    def get_user(self, user_id):
        try:
            user = StudentModel.objects.get(id=user_id)
            if user.is_active:
                return user
            return None
        except StudentModel.DoesNotExist:
            logging.getLogger("error_logger").error("user with %(user_id)d not found")
            return None

class MyFacultyAuthBackend(object):
    def authenticate(self, email, password):
        try:
            fac_user = FacultyModel.objects.get(fac_gmail=email)
            if fac_user.check_password(password):
                return fac_user
            else:
                return None
        except Exception as e:
            logging.getLogger("error_logger").error(repr(e))
            return None
    def get_user(self, user_id):
        try:
            user = FacultyModel.objects.get(id=user_id)
            if user.is_active:
                return user
            return None
        except FacultyModel.DoesNotExist:
            logging.getLogger("error_logger").error("user with %(user_id)d not found")
            return None