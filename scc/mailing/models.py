from django.db import models
from mdeditor.fields import MDTextField
# Create your models here.

# post of user in school, literally just job
class Post(models.Model):
    post_name = models.CharField(max_length=64, unique=True)
    def __str__(self):
        return self.post_name

# school of user
class School(models.Model):
    school_name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.school_name
    class Meta:
        verbose_name = 'School'
        verbose_name_plural = 'Schools'

# department of user
class Department(models.Model):
    department_name = models.CharField(max_length=255)
    def __str__(self):
        return self.department_name
    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

# user model
class SCC_User(models.Model):
    service_memo_number = models.CharField(max_length=255)
    service_registration_date = models.DateField(blank=False)
    last_name = models.CharField(max_length=64, blank=False)
    first_name = models.CharField(max_length=64, blank=False)
    surname = models.CharField(max_length=64, blank=True, null=True)
    login = models.CharField(max_length=64, null=False, blank=False, unique=True)
    number = models.CharField(max_length=64, blank=True, null=True)
    spin_code = models.CharField(max_length=16, blank=True, null=True)
    researcher_id = models.CharField(max_length=16, blank=True, null=True)
    science_project = models.CharField(max_length=255, blank=True, null=True)
    science_mentor = models.CharField(max_length=255, blank=True, null=True)
    access_ip = models.CharField(max_length=255, blank=True, null=True)
    commentary = models.TextField(default='', blank=True)

    post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.id) + ' : ' + str(self.last_name) + ' ' + str(self.first_name) + ' : ' + str(self.login)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class Email_to_user(models.Model):
    user = models.ForeignKey(SCC_User, on_delete=models.CASCADE)
    email =	models.EmailField(max_length=64, blank=False, unique=True)
    def __str__(self):
        return str(self.email) + ' : ' + str(self.user)
    class Meta:
        verbose_name = 'User-email relation'
        verbose_name_plural = 'User-email relations'

class Group(models.Model):
    group_name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.group_name
    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

class Group_to_user(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(SCC_User, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.group) + ' - ' + str(self.user)
    class Meta:
        verbose_name = 'Group-user relation'
        verbose_name_plural = 'Group-user relations'

class Template(models.Model):
    template_name = models.CharField(max_length=255, blank=False, unique=True)
    template_date = models.DateTimeField(auto_now_add=True, blank=True)

    template_text = MDTextField()

    def __str__(self):
        return str(self.template_name) + ' : ' + str(self.template_date)
    class Meta:
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'

class Mailing(models.Model):
    mailing_name = models.CharField(max_length=255, blank=False)
    mailing_date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.mailing_name) + " : " + str(self.mailing_date)
    class Meta:
        verbose_name = 'Mailing_names'
        verbose_name_plural = 'Mailings_names'

class Mailing_log(models.Model):
    mailing =       models.ForeignKey(Mailing, on_delete=models.CASCADE, null=True)
    group = 		models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    user = 			models.ForeignKey(SCC_User, on_delete=models.CASCADE, null=True)
    template = 		models.ForeignKey(Template, on_delete=models.CASCADE)
    result =        models.IntegerField()
    def __str__(self):
        return str(self.mailing)
    class Meta:
        verbose_name = 'Mailing'
        verbose_name_plural = 'Mailings'