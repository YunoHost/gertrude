from __future__ import unicode_literals

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
    print("[WIP] Here we should create the PR")

signals.change_confirmed.connect(page_edit_confirmed)


