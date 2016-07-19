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
import iidxrank.views as views
import iidxrank.views_json as views_json
import board.views as views_board

urlpatterns = [
	url(r'', include([
	# utilities (admin, imgtl ...)
	    url(r'^admin/', include(admin.site.urls)),
            url(r'^imgtl/$', views.imgtl),
            url(r'^imgdownload/$', views.imgdownload),
            url(r'^qpro/(?P<iidxid>[0-9]+)/$', views.qpro),

	# update (NOT WORKING NOW)
            url(r'^update/', include([
                    url(r'^rankedit/(?P<tablename>\w+)/$', views.rankedit, name="rankedit"),
            ])),

        # comment, board
            url(r'^board/', include([
                    url(r'^view/(?P<postid>[0-9]+)/$', views_board.view, name="postview"),
                    url(r'^modify/(?P<postid>[0-9]+)/$', views_board.modify, name="postmodify"),
                    url(r'^(?P<boardname>\w+)/$', views_board.list, name="postlist"),
                    url(r'^(?P<boardname>\w+)/(?P<page>[0-9]+)/$', views_board.list, name="postlist"),
                    url(r'^(?P<boardname>\w+)/write/$', views_board.write, name="postwrite"),
            ])),
            url(r'^songcomments/$', RedirectView.as_view(url='/songcomments/1/')),
            url(r'^songcomments/(?P<page>[0-9]+)/$', views_board.songcomments),
            url(r'^songcomment/(?P<tag>\w+)/$', views_board.songcomment),

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
            url(r'^!/(?P<tablename>\w+)/$', views.rankpage, name="rankpage"),
            url(r'^!/(?P<tablename>\w+)/detail/$', views.detailpage),
            # username
            url(r'^(?P<username>(\w|-)+)/', include([
                    url(r'^$', views.userpage),
                    url(r'^stat/recm/$', views.recommend),
                    url(r'^stat/skill/$', views.skillrank),
                    url(r'^(?P<tablename>\w+)/$', views.rankpage, name="rankpage"),
                    url(r'^(?P<tablename>\w+)/detail/$', views.detailpage),
            ])),
	])),
]
