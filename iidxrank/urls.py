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
	url(r'^iidx/update/$', views_update.index),
	url(r'^iidx/update/?(P<update>\w+)/$', views_update.startUpdate),
	url(r'^iidx/update/status/$', views_update.recentStatus),
	url(r'^iidx/update/send/$', views_update.sendMessage),
	url(r'^iidx/update/rank/$', views_update.rankupdate),
    url(r'^iidx/admin/', include(admin.site.urls)),
	url(r'^iidx/imgtl/$', views.imgtl),
	url(r'^iidx/songcomment/all/(?P<page>[0-9]+)/$', views.songcomment_all),
	url(r'^iidx/songcomment/(?P<ranktablename>\w+)/(?P<songid>[0-9]+)/(?P<difftype>\w+)/(?P<page>[0-9]+)/$', views.songcomment, name="songcomment"),
	url(r'^iidx/comment/(?P<boardid>[0-9])/$', views.board),
	url(r'^iidx/selectmusic/(?P<mode>\w+)/$', views.selectmusic),

# common urls
	url(r'^iidx/$', views.mainpage),
	url(r'^iidx/(?P<username>\w+)/$', views.userpage),
	url(r'^iidx/(?P<username>\w+)/(?P<diff>\w+)/(?P<level>\w+)/$', views.rankpage),
]
