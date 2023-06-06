from django.contrib import admin
from .models import *
from .forms import *
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Register your models here.

class UserAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'service_memo_number',
		'service_registration_date',
		'post',
		'last_name',
		'first_name',
		'surname',
		'login',
		'school',
		'department',
		'number',
		'spin_code',
		'researcher_id',
		'science_project',
		'science_mentor',
		'access_ip',
		'commentary',
	)

admin.site.register(SCC_User, UserAdmin)


class GroupToUserAdmin(admin.ModelAdmin):
	list_display = (
		'group',
		'user_id',
		'login',
		'last_name',
		'first_name',
		'surname',
		'post',
		'department',
	)

	def user_id(self, instance):
		return instance.user.id
	def login(self, instance):
		return instance.user.login
	def last_name(self, instance):
		return instance.user.last_name
	def first_name(self, instance):
		return instance.user.first_name
	def surname(self, instance):
		return instance.user.surname
	def post(self, instance):
		return instance.user.post
	def department(self, instance):
		return instance.user.department

admin.site.register(Group_to_user, GroupToUserAdmin)


class EmailToUserAdmin(admin.ModelAdmin):
	list_display = (
		'email',
		'user_id',
		'login',
		'last_name',
		'first_name',
		'surname',
		'post',
		'department',
	)


	def user_id(self, instance):
		return instance.user.id
	def login(self, instance):
		return instance.user.login
	def last_name(self, instance):
		return instance.user.last_name
	def first_name(self, instance):
		return instance.user.first_name
	def surname(self, instance):
		return instance.user.surname
	def post(self, instance):
		return instance.user.post
	def department(self, instance):
		return instance.user.department

admin.site.register(Email_to_user, EmailToUserAdmin)


admin.site.register(Post)
admin.site.register(School)
admin.site.register(Department)
admin.site.register(Group)
admin.site.register(Template)
admin.site.register(Mailing_log)
admin.site.register(Mailing)


