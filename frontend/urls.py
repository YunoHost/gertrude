from django.conf.urls import url
from django.shortcuts import redirect
from django.urls import include

from . import views

app_name = "gertrude"
urlpatterns = [
    url(r'^images/(.*)$', views.redirect_images_to_media, name=''),
    url(r'^i18n.json$', lambda request: redirect("/static/i18n.json"), name=''),
    url(r'^config.json$', lambda request: redirect("/static/config.json"), name=''),
    url(r'^_pages/(.*)$', views.get_raw_markdown, name=''),
    url(r'^submit_page_change$', views.submit_page_change),
    url(r'^confirm/', include('generic_confirmation.urls',
        namespace='generic_confirmation'),
        name="confirm"),
    url(r'^(.*)$', views.get_page, name=''),
]
