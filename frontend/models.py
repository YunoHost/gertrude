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
    content = models.CharField(max_length=50000, null=True)
    email = models.EmailField(null=True)
    descr = models.CharField(max_length=150, null=True)

    def __str__(self):
        return "Page %s edit from %s" % (self.page, self.email)

class PageEditForm(DeferredForm):
    class Meta:
        model = PageEdit
        fields = [ "page", "content", "email", "descr" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True

    def save(self, *args, **kwargs):

        # TODO/FIXME : validate that page is a file name (alphanumcharacter and
        # _ but nothing else ! (no space, no slash, no punctuation !))

        super().save(*args, **kwargs)

    def send_notification(self, user=None, instance=None, **kwargs):

        confirm_url = settings.CONFIRM_URL.format(token=instance.token)

        send_mail("[YunoHost doc] Please confirm your submission !",
                  render_to_string("confirm_mail.txt", { 'confirm_url': confirm_url }),
                  from_email="test@yunohost.org",
                  recipient_list=[self.cleaned_data['email'],])



def page_edit_confirmed(sender, instance, **kwargs):
    instance.confirmed = False
    instance.save()
    descr = instance.form_input["descr"]
    page = instance.form_input["page"]
    email = instance.form_input["email"]
    content = instance.form_input["content"]
    print("Confirming edition")
    print("[WIP] Here we should create the PR")

signals.change_confirmed.connect(page_edit_confirmed)


