from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = 'employees'

    def ready(self):
        from .signals import delete_prefecture_employee_corresponding_user, \
            delete_region_employee_corresponding_user
