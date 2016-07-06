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
	url(r'', include([
	# utilities (admin, imgtl ...)
	    url(r'^admin/', include(admin.site.urls)),
            url(r'^imgtl/$', views.imgtl),
            url(r'^qpro/(?P<iidxid>[0-9]+)/$', views.qpro),

	# update (NOT WORKING NOW)
            url(r'^update/', include([
                    url(r'^$', views_update.index),
                    url(r'^status/$', views_update.status),
                    url(r'^status/json/$', views_update.json_status),
                    # username
                    url(r'^user/(?P<username>(\w|-)+)/$', views_update.json_update_player),
                    url(r'^user_status/(?P<username>(\w|-)+)/$', views_update.json_update_player_status),
                    url(r'^rank/$', views_update.rankupdate),
                    url(r'^(?P<update>(\w|-)+)/$', views_update.update),
            ])),

    # comment, board
            url(r'^songcomment/', include([
                    url(r'^all/$', views.songcomment_all),
                    url(r'^all/(?P<page>[0-9]+)/$', views.songcomment_all),
                    url(r'^(?P<ranktablename>\w+)/(?P<songid>[0-9]+)/$', views_board.songcomment, name="songcomment"),
            ])),
            url(r'^board/', include([
                    url(r'^(?P<boardid>[0-9]+)/$', views_board.board),
                    url(r'^(?P<boardid>[0-9]+)/(?P<boardpage>[0-9]+)/$', views_board.board, name="board"),
            ])),

    # select music
            url(r'^musiclist/$', views.musiclist),
            url(r'^json/', include([
                    url(r'^musiclist/(?P<type>\w+)/level/(?P<level>[0-9]+)/$', views_json.json_level),
                    url(r'^musiclist/(?P<type>\w+)/series/(?P<series>\w+)/$', views_json.json_series),
                    url(r'^userlist/$', views_json.json_user),
                    # username
                    url(r'^recommend/(?P<username>(\w|-)+)/(?P<type>\w+)/$', views_json.json_recommend),
                    url(r'^recommend/(?P<username>(\w|-)+)/(?P<type>\w+)/(?P<level>[0-9]+)/$', views_json.json_recommend),
            ])),

    # common urls (mainpage, userpage, rankpage)
            url(r'^$', views.mainpage),
            #url(r'^!/$', RedirectView.as_view(url='/')),
            url(r'^!/$', views.userpage),
            url(r'^!/songrank/$', views.songrank),
            url(r'^!/userrank/$', views.userrank),
            url(r'^!/(?P<diff>\w+)/(?P<level>\w+)/$', views.rankpage, name="rankpage"),
            # username
            url(r'^(?P<username>(\w|-)+)/', include([
                    url(r'^$', views.userpage),
                    url(r'^stat/recm/$', views.recommend),
                    url(r'^stat/skill/$', views.skillrank),
                    url(r'^(?P<diff>\w+)/(?P<level>\w+)/$', views.rankpage, name="rankpage"),
            ])),
	])),
]
