# https://docs.djangoproject.com/en/1.9/intro/tutorial02/

from django.contrib import admin
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
  list_display = ('iidxmeid', 'iidxid', 'splevel', 'dplevel', 'spclass', 'dpclass', 'time')
  search_fields = ['iidxid', 'iidxmeid']
class SongAdmin(admin.ModelAdmin):
  list_display = ('songtitle', 'songtype', 'songlevel')
  search_fields = ['songtitle', 'songtype']

# register
admin.site.register(models.RankTable, RankTableAdmin)
admin.site.register(models.RankCategory, RankCategoryAdmin)
admin.site.register(models.RankItem, RankItemAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Song, SongAdmin)

