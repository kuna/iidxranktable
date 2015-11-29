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
from django.views.generic import RedirectView
import views, views_board
import views_update
import views_json

urlpatterns = [
# utilities (admin, imgtl ...)
    url(r'^iidx/admin/', include(admin.site.urls)),
	url(r'^iidx/imgtl/$', views.imgtl),
	url(r'^iidx/qpro/(?P<iidxid>[0-9]+)/$', views.qpro),

# update (NOT WORKING NOW)
	url(r'^iidx/update/$', views_update.index),
	url(r'^iidx/update/?(P<update>\w+)/$', views_update.startUpdate),
	url(r'^iidx/update/status/$', views_update.recentStatus),
	url(r'^iidx/update/send/$', views_update.sendMessage),
	url(r'^iidx/update/rank/$', views_update.rankupdate),

# comment, board
	url(r'^iidx/songcomment/all/$', views.songcomment_all),
	url(r'^iidx/songcomment/all/(?P<page>[0-9]+)/$', views.songcomment_all),
	url(r'^iidx/songcomment/(?P<ranktablename>\w+)/(?P<songid>[0-9]+)/$', views_board.songcomment, name="songcomment"),
	url(r'^iidx/board/(?P<boardid>[0-9]+)/$', views_board.board),
	url(r'^iidx/board/(?P<boardid>[0-9]+)/(?P<boardpage>[0-9]+)/$', views_board.board, name="board"),

# select music
	url(r'^iidx/selectmusic/$', views.selectmusic),
	url(r'^iidx/json/selectmusic/(?P<type>\w+)/level/(?P<level>[0-9]+)/$', views_json.json_level),
	url(r'^iidx/json/selectmusic/(?P<type>\w+)/series/(?P<series>\w+)/$', views_json.json_series),

# common urls (mainpage, userpage, rankpage)
	url(r'^iidx/$', views.mainpage),
	url(r'^iidx/!/$', RedirectView.as_view(url='/iidx/')),
	url(r'^iidx/(?P<username>\w+)/$', views.userpage),
	url(r'^iidx/(?P<username>.+)/(?P<diff>\w+)/(?P<level>\w+)/$', views.rankpage, name="rankpage"),
]
