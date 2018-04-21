from __future__ import unicode_literals

import os
import re
import subprocess
import requests
import json

from filelock import Timeout, FileLock

from django import forms
from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from generic_confirmation import signals
from generic_confirmation.forms import DeferredForm


class PageEdit(models.Model):
    page = models.CharField(max_length=100, null=True)
    patch = models.CharField(max_length=5000, null=True)
    email = models.EmailField(null=True)
    comment = models.CharField(max_length=150, null=True)
    date = models.DateTimeField(null=True)

    def __str__(self):
        return "Page %s edit from %s" % (self.page, self.email)

class PageEditForm(DeferredForm):
    class Meta:
        model = PageEdit
        fields = [ "page", "patch", "email", "comment", "date" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    def clean_page(self):
        page = self.cleaned_data['page']
        if not re.compile("^\w+$").match(page):
            raise ValidationError("This is not a valid page name !")
        return page

    def clean_patch(self):
        patch = self.cleaned_data['patch']
        if len(patch) == 0:
            raise ValidationError("Invalid patch ?")
        return patch

    def send_notification(self, user=None, instance=None, **kwargs):

        confirm_url = settings.CONFIRM_URL.format(token=instance.token)

        send_mail("[YunoHost doc] Please confirm your submission !",
                  render_to_string("confirm_mail.txt", { 'confirm_url': confirm_url }),
                  from_email="test@yunohost.org",
                  recipient_list=[self.cleaned_data['email'],])


def page_edit_confirmed(sender, instance, **kwargs):

    instance.confirmed = False
    instance.save()
    comment = instance.form_input["comment"]
    page = instance.form_input["page"]
    patch = instance.form_input["patch"]
    date = instance.form_input["date"]

    print("Confirming edition")

    create_PR(page, comment, date, patch)


signals.change_confirmed.connect(page_edit_confirmed)


def create_PR(page, comment, date, patch):

    cwd = os.path.join(settings.BASE_DIR, "./.git_content_botfork")
    branch = date.strftime("anonymous-%y-%m-%d_%H-%M-%S")

    lock_path = cwd+".lock"
    lock = FileLock(lock_path, timeout=5)
    with lock:

        # Reset bot fork repo to origin/master

        subprocess.Popen("git checkout master".split(), cwd=cwd).communicate()
        subprocess.Popen("git pull origin master".split(), cwd=cwd).communicate()
        subprocess.Popen("git reset --hard origin/master".split(), cwd=cwd).communicate()

        # Create branch (delete it if it already exists)

        if os.system("git -C {} branch --list | grep -q ' {}$'".format(cwd, branch)) == 0:
            subprocess.Popen("git branch -D {}".format(branch).split(),
                             cwd=cwd).communicate()

        subprocess.Popen("git checkout -b {}".format(branch).split(),
                         cwd=cwd).communicate()

        # Apply patch on a new branch

        p = subprocess.Popen("git apply".split(), cwd=cwd,
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE)
        p.stdin.write(patch.encode('utf-8'))
        stdout, stderr = p.communicate()
        p.stdin.close()
        try:
            assert p.returncode == 0
        except:
            print(stdout.decode('utf-8'))
            print(stderr.decode('utf-8'))
            raise Exception("Error while trying to apply the patch :s")

        # The patch does actually something weird : it removes the previous
        # page and the new page is "-" so we fix this ...
        subprocess.Popen("mv - {}.md".format(page).split(),
                         cwd=cwd).communicate()

        # Commit and push

        env = os.environ.copy()
        env["GIT_AUTHOR_NAME"] = settings.BOT_NAME
        env["GIT_AUTHOR_EMAIL"] = settings.BOT_EMAIL
        env["GIT_COMMITTER_NAME"] = settings.BOT_NAME
        env["GIT_COMMITTER_EMAIL"] = settings.BOT_EMAIL

        subprocess.Popen("git commit -a -m".split() + [comment],
                         cwd=cwd, env=env).communicate()

        subprocess.Popen("git push origin {} --force".format(branch).split(),
                         cwd=cwd, env=env).communicate()

        # Create the PR

        api_url = "https://api.github.com/repos/{repo}/pulls" \
                 .format(repo=settings.BOT_PR_DESTINATION)

        PR = { "title": "[Anonymous contrib] "+comment,
               "head": settings.BOT_LOGIN + ":" + branch,
               "base": "master",
               "maintainer_can_modify": True
             }

        with requests.Session() as s:
            s.headers.update({"Authorization": "token {}".format(settings.BOT_TOKEN)})
            s.post(api_url, json.dumps(PR))

