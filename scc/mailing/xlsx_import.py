from django.core.validators import validate_email
from .models import *
import openpyxl
import datetime


# import data from lsm query
class Importer:
    def load_from_xlsx(ws):
        prev_memo_number = ''
        for row in ws.iter_rows(2):
            if all(c.value is None for c in row):
                break
            
            emails = []
            groups = []
            service_memo_number = ''
            service_registration_date = ''
            first_name = ''
            last_name = ''
            post = None
            surname = ''
            login = ''
            school = None
            department = None
            number = ''
            spin_code = ''
            researcher_id = ''
            science_project = ''
            science_mentor = ''
            access_ip = ''


            for c in row:
                column_name = ws.cell(row=1, column=c.column).value

                if column_name == 'Номер служебной записки':
                    if c.value is not None:
                        prev_memo_number = c.value
                    service_memo_number = prev_memo_number
                elif column_name == 'Дата регистрации служебной записки':
                    date = str(c.value).split(' ')[0]
                    service_registration_date = date
                elif column_name == 'Имя':
                    first_name = c.value
                elif column_name == 'Фамилия':
                    last_name = c.value
                elif column_name == 'Должность':
                    post, _ = Post.objects.get_or_create(post_name=c.value)
                elif column_name == 'Отчество':
                    surname = c.value
                elif column_name == 'Логин':
                    login = c.value
                elif column_name == 'Высшая школа/Институт':
                    school, _ = School.objects.get_or_create(school_name=c.value)
                elif column_name == 'Кафедра/Подразделение':
                    department, _ = Department.objects.get_or_create(department_name=c.value)
                elif column_name == 'Контактный телефон':
                    number = c.value
                elif column_name == 'Электронная почта':
                    email_list = c.value.split(' ')
                    for e in email_list:
                        try:
                            validate_email(e)
                            emails.append(e)
                        except: 
                            pass
                elif column_name == 'SPIN-код РИНЦ':
                    spin_code = c.value
                elif column_name == 'Researcher ID WoS':
                    researcher_id = c.value
                elif column_name == 'Название научного проекта':
                    science_project = c.value
                elif column_name == 'Научный руководитель проекта':
                    science_mentor = c.value
                elif column_name == 'IP доступа к лицензиям':
                    access_ip = c.value
                elif 'Есть/Требуется логин' in column_name:
                    spt = column_name.split(' ')
                    if c.value == True:
                        groups.append(Group.objects.get_or_create(group_name=spt[0])[0])

            new_user = SCC_User.objects.filter(login__exact=login)
            if not new_user.exists():
                new_user = SCC_User.objects.create(service_memo_number=service_memo_number,
                                                service_registration_date=service_registration_date,
                                                first_name=first_name,
                                                last_name=last_name,
                                                surname=surname,
                                                login=login,
                                                post=post,
                                                school = school,
                                                department = department,
                                                number=number,
                                                spin_code=spin_code,
                                                researcher_id=researcher_id,
                                                science_project=science_project,
                                                science_mentor=science_mentor,
                                                access_ip=access_ip
                )
            else:
                new_user = new_user[0]

            for email in emails:
                if not Email_to_user.objects.filter(email__exact=email).exists():
                    Email_to_user.objects.create(user=new_user, email=email)
            
            for group in groups:
                Group_to_user.objects.get_or_create(group=group, user=new_user)




