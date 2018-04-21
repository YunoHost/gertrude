import os
import sys
import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        for key in [ "BOT_REPO", "BOT_LOGIN", "BOT_TOKEN" ]:
            assert hasattr(settings, key), \
                   "You need to specify the {} variable in your settings before using this command".format(key)

        git_path = os.path.join(settings.BASE_DIR, ".git_content_botfork")

        if os.path.exists(git_path):
            subprocess.check_call("rm -rf {}".format(git_path), shell=True)

        github_repo = "https://github.com/" + settings.BOT_REPO
        subprocess.check_call("git clone %s %s" % (github_repo, git_path), shell=True)
        subprocess.check_call("git remote rm origin", shell=True, cwd=git_path)
        subprocess.check_call("git remote add origin https://{login}:{token}@github.com/{repo}" \
                              .format(login=settings.BOT_LOGIN,
                                      token=settings.BOT_TOKEN,
                                      repo=settings.BOT_REPO),
                              shell=True, cwd=git_path)
