from django.urls import path, include
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.decorators import login_required
from .views import *

app_name='mailing'

url_users = [
	path('', login_required(UserListView.as_view()), name='users'),
    path('create', login_required(UserCreateView.as_view()), name='create'),
	path('edit/<ids>', login_required(UserUpdateView.as_view()), name='users-edit'),
    path('edit-send/post', login_required(UserUpdateView.ajax_post), name='post-ajax'),
    path('edit-send/school', login_required(UserUpdateView.ajax_school), name='school-ajax'),
    path('edit-send/department', login_required(UserUpdateView.ajax_department), name='department-ajax'),
]

url_groups = [
    path('', login_required(GroupListView.as_view()), name='groups'),
    path('group-create', login_required(GroupCreateView.as_view()), name='group-create'),
    path('group-edit/<int:id>', login_required(GroupUpdateView.as_view()), name='group-edit'),
]

url_templates = [
    path('', login_required(TemplateListView.as_view()), name='templates'),
    path('create', login_required(TemplateCreateView.as_view()), name='template-create'),
    path('edit/<int:id>', login_required(TemplateUpdateView.as_view()), name='template-edit'),
]

url_mailing = [
    path('', login_required(MailingSendView.as_view()), name='mailing'),
    path('maling-send/group', login_required(MailingSendView.ajax_selected_groups), name='groups-ajax'),
]

url_logs = [
    path('', login_required(MailingListView.as_view()), name='logs'),
    path('details/<int:id>', login_required(MailingDetailView.as_view()), name='details'),

]

urlpatterns = [
	path('', login_required(TemplateView.as_view(template_name='mailing_index.html')), name='index'),
	path('start/', include(url_mailing)),
    path('logs/', include(url_logs)),
    path('templates/', include(url_templates)),
	path('groups/', include(url_groups)),
	path('users/', include(url_users)),
]
