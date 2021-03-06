import os
import re
import subprocess
import datetime

# from markdown2 import markdown_path
from markdown import markdownFromFile

from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .models import PageEditForm


def get_raw_markdown(request, file_name):
    autorized_files_list = []
    for i in os.listdir(os.path.join(settings.BASE_DIR, "git_content")):
        if os.path.isdir(i):
            continue

        if not i.endswith(".md"):
            continue

        autorized_files_list.append(i)

    if file_name in ("", "/"):
        file_name = "index"

    if file_name not in autorized_files_list:
        raise Http404

    return HttpResponse(open(os.path.join(settings.BASE_DIR, "git_content", file_name), "r"))


def get_page(request, file_name):
    autorized_files_list = []
    for i in os.listdir(os.path.join(settings.BASE_DIR, "git_content")):
        if os.path.isdir(i):
            continue

        if not i.endswith(".md"):
            continue

        autorized_files_list.append(i.rstrip(".md"))

    if file_name in ("", "/"):
        file_name = "index"

    if file_name not in autorized_files_list:
        raise Http404

    # html = markdown_path(os.path.join(settings.BASE_DIR, "git_content", file_name + ".md"))
    try:
        # Python2
        from StringIO import StringIO
        html = StringIO()
    except ImportError:
        # Python3
        from io import BytesIO
        html = BytesIO()
    markdownFromFile(input=os.path.join(settings.BASE_DIR, "git_content", file_name + ".md"), output=html)

    html.read()

    return render(request, "index.html", {
        "content": html.getvalue(),
    })


def redirect_images_to_media(request, image):
    return redirect(settings.MEDIA_URL + "images/" + image)

@require_POST
def submit_page_change(request):

    patch = get_diff(request.POST.get("page", ""),
                     request.POST.get("content", ""))
    form = PageEditForm({"page": request.POST.get("page", ""),
                         "patch": patch,
                         "comment": request.POST.get("descr", ""),
                         "email": request.POST.get("email", ""),
                         "date": datetime.datetime.now()})
    if form.is_valid():
        form.save()
        return HttpResponse('')

    error_html = [ "<strong>{key}</strong>: {message}".format(key=key,
                                                              message=', '.join(message))
                   for key, message in form.errors.items() ]
    error_html = "<br>".join(error_html)
    return HttpResponseForbidden(error_html)


def get_diff(page, content):
    if not re.compile("^\w+$").match(page):
        return ""

    p = subprocess.Popen(["git", "diff", "--no-index", "--", page+".md", "-" ],
                         cwd="./git_content",
                         stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE)
    p.stdin.write(content.encode('utf-8'))
    diff = p.communicate()[0].decode('utf-8')
    p.stdin.close()
    return diff
