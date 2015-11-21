# https://docs.djangoproject.com/en/1.9/intro/tutorial02/

from django.contrib import admin
import models

# form
class RankTableAdmin(admin.ModelAdmin):
	list_display = ('tabletitle', 'tablename', 'time')
class RankCategoryAdmin(admin.ModelAdmin):
	list_display = ('categoryname', 'get_tabletitle')
	search_fields = ['ranktable__tabletitle']
class RankItemAdmin(admin.ModelAdmin):
	list_display = ('get_categoryname', 'get_songtitle', 'get_songtype', 'get_songlevel', 'info')
	search_fields = ['song__title']
class PlayerAdmin(admin.ModelAdmin):
	list_display = ('iidxmeid', 'iidxid', 'splevel', 'dplevel', 'spclass', 'dpclass', 'time')
class SongAdmin(admin.ModelAdmin):
	list_display = ('songtitle', 'songtype', 'songlevel')

# register
admin.site.register(models.RankTable, RankTableAdmin)
admin.site.register(models.RankCategory, RankCategoryAdmin)
admin.site.register(models.RankItem, RankItemAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Song, SongAdmin)
