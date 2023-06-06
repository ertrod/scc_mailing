from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.forms.models import model_to_dict
import json
import mammoth
import io
import markdown
import openpyxl
from .xlsx_import import *
from .classes import *
from .models import *
from .forms import *


class UserListView(ListView): # add search
    model = SCC_User
    context_object_name = 'user_list'
    template_name = 'mailing_users.html'
    paginate_by = 50

    def get(self, request):
        users = self.model.objects.all()
        data = Actions.get_user_info(users)

        # paginate data (recomennded to be ordered)
        # paginator = Paginator(data, self.paginate_by)
        # page = request.GET.get('page')

        # try:
        #     paginated = paginator.get_page(page)
        # except PageNotAnInteger:
        #     paginated = paginator.get_page(1)
        # except EmptyPage:
        #     paginated = paginator.get_page(paginator.num_pages)

        return render(request, self.template_name, {
            'DataPaginated': data,
            # 'paginate_by': self.paginate_by
        })

    def post(self, request):
        if request.POST.get('Edit'):
            users_id = request.POST.getlist('checked-users')
            if users_id:
                return redirect('mailing:users-edit', ids=users_id)
        if request.POST.get('Create'):
            return redirect('mailing:create')
        if request.POST.get('Remove'):
            users_id = request.POST.getlist('checked-users')
            if (users_id):
                users_id = [int(x) for x in users_id]
                self.model.objects.filter(id__in=users_id).delete()
        if request.POST.get('Back'):
            return redirect('mailing:index')
        if request.POST.get('Import') and request.FILES:
            file = request.FILES['File']
            _, extension = os.path.splitext(file.name)
            bytes = io.BytesIO(file.read())
            if extension == '.xlsx':
                wrkbook = openpyxl.load_workbook(bytes)
                ws = wrkbook.active
                Importer.load_from_xlsx(ws)


        return redirect('mailing:users')


class UserCreateView(CreateView):
    model = SCC_User
    fields = '__all__'
    template_name = 'mailing_users_create.html'

    def get(self, request):
        user_form = {}
        user_form['form'] = UserUpdateForm()

        groups = Group.objects.all()

        posts = Post.objects.all()
        schools = School.objects.all()
        departments = Department.objects.all()

        return render(request, self.template_name, {
            'user_form': user_form,
            'groups': groups,
            'posts': posts,
            'schools': schools,
            'departments': departments,
        })

    def post(self, request):
        if request.POST.get('Confirm') or request.POST.get('Add-another'):
            form = UserUpdateForm(request.POST)
            if form.is_valid():
                form.save()
                new_user = self.model.objects.latest('id')

                # groups
                checked_groups = request.POST.getlist('checked-groups-new')
                checked_groups = list(map(int, checked_groups))

                for c in checked_groups:
                    group = Group.objects.get(pk=c)
                    Group_to_user(group=group, user=new_user).save()

                #foreign keys
                post = request.POST.get('post')
                department = request.POST.get('department')
                school = request.POST.get('school')

                try:
                    new_user.post = Post.objects.get_or_create(post_name=post)[0]
                    new_user.school = School.objects.get_or_create(school_name=school)[0]
                    new_user.department = Department.objects.get_or_create(department_name=department)[0]
                    
                    new_user.save()
                except Exception as e: # handle error in future 
                    print(e)

                # emails
                new_emails = request.POST.getlist('new-email')
                for email in new_emails:
                    if email:
                        Email_to_user(user_id=new_user.id, email=email).save()
            if request.POST.get('Add-another'):
                return redirect('mailing:create')

        return redirect('mailing:users')


class UserUpdateView(UpdateView):
    model = SCC_User
    template_name = 'mailing_users_edit.html'

    def get(self, request, ids):
        ids = Actions.string_list_to_list(ids)
        users = Actions.get_user_info(self.model.objects.filter(id__in=ids))
        groups = Group.objects.all()

        posts = Post.objects.all()
        schools = School.objects.all()
        departments = Department.objects.all()

        data = []
        for u in users:
            user_data = dict()
            user_data['id'] = u['user'].id
            user_data['form'] = UserUpdateForm(
                instance=u['user'], prefix=user_data['id'])
            
            group_data = []
            for g in groups:
                group_info = {
                    'group': g,
                    'is_in': Group_to_user.objects.filter(group__exact=g.id, user__exact=u['user'].id).exists()
                }
                group_data.append(group_info)
            user_data['group'] = group_data

            if posts.filter(post_name__exact=u['user'].post).exists():
                user_data['post'] = {
                    'id': posts.filter(post_name__exact=u['user'].post).values('id')[0]['id'],
                    'name': u['user'].post
                }
            if schools.filter(school_name__exact=u['user'].school).exists():
                user_data['school'] = {
                    'id': schools.filter(school_name__exact=u['user'].school).values('id')[0]['id'],
                    'name': u['user'].school
                }
            if departments.filter(department_name__exact=u['user'].department).exists():
                user_data['department'] = {
                    'id': departments.filter(department_name__exact=u['user'].department).values('id')[0]['id'],
                    'name': u['user'].department
                }
            user_data['emails'] = u['emails']
            data.append(user_data)

        return render(request, self.template_name, {
            'user_forms': data,
            'posts': posts,
            'schools': schools,
            'departments': departments,

        })

    def post(self, request, ids):
        ids = Actions.string_list_to_list(ids)

        for i in ids:
            form = UserUpdateForm(
                request.POST, instance=get_object_or_404(self.model, pk=i), prefix=i)
            if form.is_valid():
                form.save()

                #groups
                checked_groups = request.POST.getlist('checked-groups-' + str(i))
                checked_groups = list(map(int, checked_groups))

                excluded_groups = Group_to_user.objects.filter(user__exact=i).exclude(group__in=checked_groups)
                excluded_groups.delete()

                for c in checked_groups:
                    if not Group_to_user.objects.filter(group__exact=c, user__exact=i).exists():
                        group = Group.objects.get(pk=c)
                        user = SCC_User.objects.get(pk=i)
                        Group_to_user(group=group, user=user).save()

                # foreign keys
                post = request.POST.get('post' + str(i))
                department = request.POST.get('department' + str(i))
                school = request.POST.get('school' + str(i))

                try:
                    user = get_object_or_404(self.model, pk=i)
                    # get only instance
                    user.post = Post.objects.get_or_create(post_name=post)[0]
                    user.school = School.objects.get_or_create(school_name=school)[0]
                    user.department = Department.objects.get_or_create(department_name=department)[0]
                    
                    user.save()
                except Exception as e: # handle error in future 
                    print(e)
                    

                # emails
                emails_before = Email_to_user.objects.filter(
                    user_id__exact=i).values_list('id', flat=True)
                emails_before = list(emails_before)

                old_emails = request.POST.getlist('email' + str(i))
                old_emails_ids = request.POST.getlist('email-id' + str(i))
                old_emails_ids = [int(x) for x in old_emails_ids]
                deleted_emails = list(set(emails_before)-set(old_emails_ids))
                Email_to_user.objects.filter(id__in=deleted_emails).delete()

                email_dict = dict(zip(old_emails_ids, old_emails))
                for id in old_emails_ids:
                    Email_to_user.objects.filter(
                        id__exact=id).update(email=email_dict[id])

                new_emails = request.POST.getlist('new-email' + str(i))
                for email in new_emails:
                    if email and not Email_to_user.objects.filter(email__exact=email).exists():
                        Email_to_user(user_id=i, email=email).save()
        return redirect('mailing:users')
    
    def ajax_post(request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            data = json.load(request)
            post = data['post']

            if request.method == "POST":
                if data['op'] == 'create':
                    is_exist = False
                    new_post, created = Post.objects.get_or_create(post_name=data['post'])
                    is_exist = not created
                    return JsonResponse({
                        'status': 'post created',
                        'exists': is_exist,
                        'value': new_post.post_name,
                        'id': new_post.id
                    })
                if data['op'] == 'update':
                    post = None
                    try:
                        post = Post.objects.filter(id__exact=data['id'])[0]
                        post.post_name = data['post']
                        post.save()
                    except Exception as e:
                        print(e)
                        response = JsonResponse({"error": "error with updating post"})
                        response.status_code = 403
                        return response

                    return JsonResponse({
                        'status': 'post updated',
                        'value': post.post_name,
                        'id': post.id,
                    })
                if data['op'] == 'delete':
                    try:
                        Post.objects.filter(id__exact=data['id']).delete()
                    except:
                        response = JsonResponse({"error": "error with deleting post"})
                        response.status_code = 403
                        return response

                    return JsonResponse({'status': 'post deleted'})

    def ajax_school(request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            data = json.load(request)
            school = data['school']

            if request.method == "POST":
                if data['op'] == 'create':
                    is_exist = False
                    new_school, created = School.objects.get_or_create(school_name=data['school'])
                    is_exist = not created
                    return JsonResponse({
                        'status': 'school created',
                        'exists': is_exist,
                        'value': new_school.school_name,
                        'id': new_school.id
                    })
                if data['op'] == 'update':
                    school = None
                    try:
                        school = School.objects.filter(id__exact=data['id'])[0]
                        school.school_name = data['school']
                        school.save()
                    except Exception as e:
                        print(e)
                        response = JsonResponse({"error": "error with updating school"})
                        response.status_code = 403
                        return response

                    return JsonResponse({
                        'status': 'school updated',
                        'value': school.school_name,
                        'id': school.id,
                    })
                if data['op'] == 'delete':
                    try:
                        School.objects.filter(id__exact=data['id']).delete()
                    except:
                        response = JsonResponse({"error": "error with deleting School"})
                        response.status_code = 403
                        return response

                    return JsonResponse({'status': 'school deleted'})

    def ajax_department(request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            data = json.load(request)
            department = data['department']

            if request.method == "POST":
                if data['op'] == 'create':
                    is_exist = False
                    new_department, created = Department.objects.get_or_create(department_name=data['department'])
                    is_exist = not created
                    return JsonResponse({
                        'status': 'department created',
                        'exists': is_exist,
                        'value': new_department.department_name,
                        'id': new_department.id
                    })
                if data['op'] == 'update':
                    department = None
                    try:
                        department = Department.objects.filter(id__exact=data['id'])[0]
                        department.department_name = data['department']
                        department.save()
                    except Exception as e:
                        print(e)
                        response = JsonResponse({"error": "error with updating department"})
                        response.status_code = 403
                        return response

                    return JsonResponse({
                        'status': 'department updated',
                        'value': department.department_name,
                        'id': department.id,
                    })
                if data['op'] == 'delete':
                    try:
                        Department.objects.filter(id__exact=data['id']).delete()
                    except:
                        response = JsonResponse({"error": "error with deleting department"})
                        response.status_code = 403
                        return response

                    return JsonResponse({'status': 'department deleted'})


class GroupListView(ListView):
    model = Group
    template_name = 'mailing_groups.html'

    def get(self, request):
        data = []
        groups = Group.objects.all()

        for g in groups:
            group = {}
            users = Group_to_user.objects.filter(group__exact=g.id)
            group = {
                'group': g,
                'users': users,
            }
            data.append(group)

        return render(request, self.template_name, {'group_list': data})
    
    def post(self, request):
        if request.POST.get('Edit'):
            group_id = request.POST.get('Edit')
            return redirect('mailing:group-edit', group_id)
        if request.POST.get('Create'):
            return redirect('mailing:group-create')
        if request.POST.get('Back'):
            return redirect('mailing:index')


class GroupCreateView(CreateView):
    model = Group
    template_name = 'mailing_groups_create.html'

    def get(self, request):
        group_form = GroupUpdateForm()
        return render(request, self.template_name, {
            'group': group_form,
        })
    def post(self, request):
        form = GroupUpdateForm(request.POST)
        if form.is_valid():
            form.save()
            if request.POST.get('Edit'):
                return redirect('mailing:group-edit', Group.objects.latest('id').id)
            
        return redirect('mailing:groups')


class GroupUpdateView(UpdateView):
    model = Group
    template_name = 'mailing_groups_edit.html'

    def get(self, request, id):
        instance = Group.objects.get(pk=id)
        group = {}
        group['form'] = GroupUpdateForm(instance=instance)
        group['users'] = Group_to_user.objects.filter(group__exact=instance.id)
        users = []
        users_in_group = []

        all_users = SCC_User.objects.all()
        for u in all_users:
            user = {}
            user['user'] = u
            if Group_to_user.objects.filter(group__exact=instance.id, user__exact=u.id).exists():
                user['is_in'] = True
                users_in_group.append(u)
            else:
                user['is_in'] = False

            users.append(user)

        return render(request, self.template_name, {
            'id': id,
            'group': group,
            'users_in_group': users_in_group,
            'all_users': users
        })
    
    def post(self, request, id):
        if request.POST.get('Add'):
            instance = Group.objects.get(pk=id)
            checked_users = request.POST.getlist('checked-users')
            checked_users = list(map(int, checked_users))
            if checked_users:
                previous_checked = Group_to_user.objects.filter(group__exact=instance.id)
                for u in previous_checked:
                    if not (u.user in checked_users):
                        u.delete()
                for i in checked_users:
                    if not Group_to_user.objects.filter(group__exact=instance.id, user__exact=i).exists():
                        user = SCC_User.objects.get(pk=i)
                        Group_to_user(group=instance, user=user).save()
            else:
                Group_to_user.objects.filter(group__exact=instance.id).delete()
            return redirect('mailing:group-edit', id)
        
        if request.POST.get('Delete'):
            instance = Group.objects.get(pk=id)
            Group_to_user.objects.filter(group__exact=instance.id).delete()
            instance.delete()
            return redirect('mailing:groups')
        
        if request.POST.get('Confirm'):
            instance = Group.objects.get(pk=id)
            form = GroupUpdateForm(request.POST, instance=instance)
            if form.is_valid():
                form.save() 
            return redirect('mailing:groups')
    

class TemplateListView(ListView):
    model = Template
    template_name = 'mailing_templates.html'

    def get(self, request):
        templates = Template.objects.all()
        return render(request, self.template_name, {
            'templates': templates,
        })
    
    def post(self, request):
        if request.POST.get('Edit'):
            template_id = request.POST.get('Edit')
            return redirect('mailing:template-edit', template_id)
        if request.POST.get('Create'):
            return redirect('mailing:template-create')
        if request.POST.get('Delete'):
            template_id = request.POST.get('Delete')
            self.model.objects.get(pk=template_id).delete()
            return redirect('mailing:templates')
        if request.POST.get('Back'):
            return redirect('mailing:index')

import os

class TemplateCreateView(CreateView):
    model = Template
    template_name = 'mailing_templates_create.html'

    def get(self, request):
        form = TemplateUpdateForm()

        return render(request, self.template_name, {
            'form': form
        })

    def post(self, request):
        if request.POST.get('Create'):
            form = TemplateUpdateForm(request.POST)
            if form.is_valid():
                form.save()

        if request.POST.get('Import'):
            form = TemplateUpdateForm()
            if request.FILES:
                file = request.FILES['File']
                _, extension = os.path.splitext(file.name)
                bytes = io.BytesIO(file.read())
                if extension == '.docx':
                    markdown_docx = mammoth.convert_to_markdown(bytes)
                    form.fields['template_text'].initial = markdown_docx.value
                if extension == '.txt' or extension == '.md':
                    form.fields['template_text'].initial = bytes.getvalue().decode()

            return render(request, self.template_name, {
                'form': form
            })

        return redirect('mailing:templates')


class TemplateUpdateView(UpdateView):
    model = Template
    template_name = 'mailing_templates_edit.html'

    def get(self, request, id):
        instance = self.model.objects.get(pk=id)
        form = TemplateUpdateForm(instance=instance)

        return render(request, self.template_name, {
            'form': form
        })

    def post(self, request, id):
        instance = self.model.objects.get(pk=id)
        form = TemplateUpdateForm(request.POST, instance=instance)
        if request.POST.get('Confirm'):
            if form.is_valid():
                form.save()
        if request.POST.get('Import') and request.FILES:
            file = request.FILES['File']
            _, extension = os.path.splitext(file.name)
            bytes = io.BytesIO(file.read())
            if extension == '.docx':
                markdown_docx = mammoth.convert_to_markdown(bytes)
                form.fields['template_text'].initial = markdown_docx.value
                markdown_docx = markdown_docx.value
            if extension == '.txt' or extension == '.md':
                markdown_docx = bytes.getvalue().decode()
                form.fields['template_text'].initial = markdown_docx

            form = TemplateUpdateForm(
                {'template_name': instance.template_name, 'template_text': markdown_docx}, instance=instance)

            return render(request, self.template_name, {
                'form': form
            })

        if request.POST.get('Delete'):
            instance.delete()

        return redirect('mailing:templates')

from django.template import Template as Template_from_str
from django.template import Context
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings

import exchangelib


class MailingSendView(ListView):
    model = Mailing
    template_name = 'mailing_start.html'

    def get(self, request):
        templates = Template.objects.all()
        groups = Group.objects.all()
        data = Actions.get_user_info(SCC_User.objects.all())

        return render(request, self.template_name, {
            'templates': templates,
            'groups': groups,
            'users': data,
        })
    
    def post(self, request):
        subject = request.POST.get('Subject')
        template_id = request.POST.get('Templates')
        group_ids = request.POST.getlist('checked-groups')
        user_ids = request.POST.getlist('checked-users')
        
        group_ids = list(map(int, group_ids))
        user_ids = list(map(int, user_ids))
        
        group_users = Group_to_user.objects.filter(group__in=group_ids).values('user')
        group_users = list(user['user'] for user in group_users)
        user_ids = [*user_ids, *group_users]

        users = SCC_User.objects.filter(id__in=user_ids)

        template = Template.objects.get(pk=template_id)
        html_text = Template_from_str(markdown.markdown(template.template_text))

        mailing = Mailing.objects.create(mailing_name=subject)

        group_ids = set(group_ids)

        credentials = exchangelib.Credentials((settings.USER_DOMAIN + '\\' + settings.USER_NAME), 
                                              settings.USER_PASSWORD)
        config = exchangelib.Configuration(server=settings.EMAIL_HOST, 
                                           credentials=credentials, auth_type=exchangelib.NTLM)
        account = exchangelib.Account(primary_smtp_address=settings.PRIMARY_SMTP_ADDRESS, config=config,
                                      autodiscover=False, access_type=exchangelib.DELEGATE)

        for user in users:
            data = Context(model_to_dict(user))
            user_emails = Email_to_user.objects.filter(user__exact=user.id).values('email')
            user_emails = list(e['email'] for e in user_emails)
            html_content = html_text.render(data)

            result = 0
            for email in user_emails:
                message = exchangelib.Message(account=account, subject=subject, 
                                              body=exchangelib.HTMLBody(html_content),
                                              to_recipients=[exchangelib.Mailbox(email_address=email)])
                message.send()
                result = 1

            user_group = Group_to_user.objects.filter(user__exact=user.id).values('group')
            user_group = set(g['group'] for g in user_group)
            common_group = None
            common_groups = (user_group & group_ids)
            if common_groups:
                common_group = list(common_groups)[0]
                common_group = Group.objects.get(pk=common_group)

            Mailing_log.objects.create(mailing=mailing, group=common_group, user=user, template=template, result=result)


        return redirect('mailing:index')
        
    
    def ajax_selected_groups(request):
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            data = json.load(request)
            if request.method == "POST":
                groups = Group_to_user.objects.filter(group__in=data['groups']).values('user')
                users = SCC_User.objects.exclude(id__in=groups)
                users = Actions.get_user_info(users)
                
                for u in users:
                    u['user'] = model_to_dict(u['user'])

                return JsonResponse({'users': users})


class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing_logs.html'

    def get(self, request):
        mailings = self.model.objects.all()
        return render(request, self.template_name, {
            'mailings': mailings
        })
    
    def post(self, request):
        if request.POST.get('Details'):
            mailing_id = request.POST.get('Details')
            return redirect('mailing:details', mailing_id)
        if request.POST.get('Delete'):
            mailing_id = request.POST.get('Delete')
            self.model.objects.get(pk=mailing_id).delete()
        if request.POST.get('Back'):
            return redirect('mailing:index')

        return redirect('mailing:logs')


class MailingDetailView(ListView):
    model = Mailing
    template_name = 'mailing_logs_view.html'

    def get(self, request, id):
        mailings = {}
        mailing_instance = self.model.objects.get(pk=id)
        logs = Mailing_log.objects.filter(mailing__exact=mailing_instance)
        
        if logs:
            users_ids = list(u['user'] for u in logs.values('user'))
            users = SCC_User.objects.filter(id__in=users_ids)
            users_data = Actions.get_user_info(users)
            
            for u in users_data:
                result = logs.filter(user__exact=u['user']).values('result')[0]
                u['result'] = result['result']

            template_id = logs[0].template
            template = Template.objects.get(pk=template_id.id)

            mailings['users'] = users_data
            mailings['template'] = template

        return render(request, self.template_name, {
            'mailings': mailings,
            'mailing': mailing_instance,
        })
    
    def post(self, request, id):
        if request.POST.get('Back'):
            return redirect('mailing:logs')

