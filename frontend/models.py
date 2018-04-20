from __future__ import unicode_literals

from django import forms
from django.db import models

from generic_confirmation import signals
from generic_confirmation.forms import DeferredForm


class PageEdit(models.Model):
    page = models.CharField(max_length=100, null=True)
    content = models.CharField(max_length=50000, null=True)
    email = models.EmailField(null=True)
    descr = models.CharField(max_length=150, null=True)

    def __str__(self):
        return "Page %s edit from %s" % (page, email)

class PageEditForm(DeferredForm):
    class Meta:
        model = PageEdit
        fields = [ "page", "content", "email", "descr" ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key in self.fields:
            self.fields[key].required = True




def send_notification(sender, instance, **kwargs):
    """ a signal receiver which does some tests """

    print("in send notifications")
    print(sender)  # the class which is edited
    print(instance)  # the DeferredAction
    print(instance.token)  # needed to confirm the action


signals.confirmation_required.connect(send_notification)
