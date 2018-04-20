import os

# from markdown2 import markdown_path
from markdown import markdownFromFile

from django.http import Http404, HttpResponse
from django.conf import settings
from django.shortcuts import render, redirect


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
