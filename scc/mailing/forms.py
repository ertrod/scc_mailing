from django import forms
from .models import *
from .classes import *

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = SCC_User
        fields = ['service_memo_number', 'service_registration_date', 'last_name',
            'first_name', 'surname', 'login', 'number', 'spin_code', 'researcher_id', 
            'science_project', 'science_mentor', 'access_ip', 'commentary']
        labels = {
            'service_memo_number': 'Номер служебной записки',
            'service_registration_date': 'Дата регистрации служебной записки',
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'surname': 'Отчество',
            'login': 'Логин',
            'number': 'Номер телефона',
            'spin_code': 'SPIN-код РИНЦ',
            'researcher_id': 'Researcher ID WoS',
            'science_project': 'Название научного проекта',
            'science_mentor': 'Научный руководитель',
            'access_ip': 'IP доступа к лицензиям',
            'commentary': 'Комментарий',
        }

class EmailUpdateForm(forms.ModelForm):
    class Meta:
        model = Email_to_user
        fields = '__all__'

class GroupUpdateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['group_name']
        labels = {'group_name': 'Название группы'}

class TemplateUpdateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ['template_name', 'template_text']
        labels = {
            'template_name': 'Название шаблона',
            'template_text': 'Текст шаблона'
        }

