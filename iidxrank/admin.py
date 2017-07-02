# https://docs.djangoproject.com/en/1.9/intro/tutorial02/

from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django import forms
import models

class RankCategoryInline(admin.TabularInline):
  model = models.RankCategory
  ordering = ("-sortindex",)
  extra = 3

# admin
class RankTableAdmin(admin.ModelAdmin):
  list_display = ('tabletitle', 'tablename', 'time')
  inlines = [RankCategoryInline]
class RankCategoryAdmin(admin.ModelAdmin):
  list_display = ('categoryname', 'get_tabletitle', 'get_sortindex')
  search_fields = ['ranktable__tabletitle']
class RankItemAdmin(admin.ModelAdmin):
  list_display = ('get_categoryname', 'get_songtitle', 'get_ranktablename', 'info')
  search_fields = ['song__songtitle', 'rankcategory__categoryname', 'rankcategory__ranktable__tablename']
class PlayerAdmin(admin.ModelAdmin):
  list_display = ('iidxmeid', 'iidxid', 'splevel', 'dplevel', 'spclass', 'dpclass', 'time', 'get_playrecord_count')
  search_fields = ['iidxid', 'iidxmeid']
class SongAdmin(admin.ModelAdmin):
  list_display = ('songtitle', 'songtype', 'songlevel', 'dper_actions')
  search_fields = ['songtitle', 'songtype']
  # https://medium.com/@hakibenita/how-to-add-custom-action-buttons-to-django-admin-8d266f5b0d41
  def process_dbr(self, request, songid, *args, **kwargs):
      return HttpResponse("""
      <script>
      alert('not importemented');
      history.back();
      </script>
      """)
      #return HttpResponseRedirect('/admin/iidxrank/song/')
  def get_urls(self):
      urls = super(SongAdmin, self).get_urls()
      custom_urls = [
        url(r'^(?P<songid>.+)/dbr',
        self.admin_site.admin_view(self.process_dbr),
        name='dper-dbr'),
      ]
      return custom_urls + urls
  def dper_actions(self, obj):
      return format_html(
        '<a class="button" href="{}">DBR</a>',
        reverse('admin:dper-dbr', args=[obj.pk])
        )

# register
admin.site.register(models.RankTable, RankTableAdmin)
admin.site.register(models.RankCategory, RankCategoryAdmin)
admin.site.register(models.RankItem, RankItemAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Song, SongAdmin)

