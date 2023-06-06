# additional classes
from .models import *
import itertools
import ast
import re
from django.utils.html import strip_tags


class Actions():
    # creating dictionary with user info user->userinfo, emails->user emails, groups -> user groups
    def get_user_info(users):
        data = []
        user_data = dict()
        for user in users:
            # get emails of specific user -> returns list of tuples
            emails = Email_to_user.objects.filter(user__exact=user.id).values()

            # get group ids for specific user -> returns list of tuples -> convert to list
            group_ids = list(itertools.chain(
                *(Group_to_user.objects.filter(user__exact=user.id).values_list('group'))))
            # get groups for specific user -> returns list of tuples
            groups = Group.objects.filter(id__in=group_ids).values_list('group_name')

            # convert list of tuples to list
            emails_list = list(emails)
            group_list = list(itertools.chain(*groups))

            user_data['user'] = user
            user_data['emails'] = emails_list
            user_data['groups'] = group_list
            data.append(user_data)
            user_data = dict()
        return data

    def get_user_emails(id):
        emails = Email_to_user.objects.filter(user__exact=id).values_list('email')
        return emails

    def string_list_to_list(string):
        return ast.literal_eval(string)

    def html_to_plain(html):
        text_only = re.sub('[ \t]+', ' ', strip_tags(html))
        return text_only.replace('\n ', '\n').strip()