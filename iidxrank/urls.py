"""iidxrank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
import views
import views_update

urlpatterns = [
# preoccupied urls
	url(r'^admin/update/$', views_update.index),
	url(r'^admin/update/?(P<update>\w+)/$', views_update.startUpdate),
	url(r'^admin/update/status/$', views_update.recentStatus),
	url(r'^admin/update/send/$', views_update.sendMessage),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/$', views.test),
	url(r'^iidx/imgtl/$', views.imgtl),
	url(r'^iidx/songcomment/(?P<ranktablename>\w+)/(?P<songid>[0-9]+)/(?P<difftype>\w+)/$', views.songcomment, name="songcomment"),
	url(r'^iidx/comment/(?P<boardid>[0-9])/$', views.board),

# common urls
	url(r'^iidx/$', views.mainpage),
	url(r'^iidx/(?P<username>\w+)/$', views.userpage),
	url(r'^iidx/(?P<username>\w+)/(?P<diff>\w+)/(?P<level>\w+)/$', views.rankpage),
]
