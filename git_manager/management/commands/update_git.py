import os
import sys
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        if not hasattr(settings, "GIT_URL"):
            print "You need to specify the GIT_URL variable in your settings before using this command"
            sys.exit(1)

        git_path = os.path.join(settings.BASE_DIR, "git_content")

        if not os.path.exists(git_path):
            print "git clone %s %s" % (settings.GIT_URL, git_path)
            subprocess.check_call("git clone %s %s" % (settings.GIT_URL, git_path), shell=True)
        else:
            print "git pull %s" % settings.GIT_URL
            subprocess.check_call("git pull %s" % settings.GIT_URL, shell=True, cwd=git_path)
