# https://docs.djangoproject.com/en/1.9/intro/tutorial02/

from django.contrib import admin
from django import forms
import models

# form
class BoardCommentForm(forms.ModelForm):
	class Meta:
		model = models.BoardComment
		fields = '__all__'
		widgets = {
			'text': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
		}

# admin
class RankTableAdmin(admin.ModelAdmin):
	list_display = ('tabletitle', 'tablename', 'time')
class RankCategoryAdmin(admin.ModelAdmin):
	list_display = ('categoryname', 'get_tabletitle', 'get_sortindex')
	search_fields = ['ranktable__tabletitle']
class RankItemAdmin(admin.ModelAdmin):
	list_display = ('get_categoryname', 'get_songtitle', 'get_ranktablename', 'info')
	search_fields = ['song__songtitle', 'rankcategory__categoryname', 'rankcategory__ranktable__tablename']
class PlayerAdmin(admin.ModelAdmin):
	list_display = ('iidxmeid', 'iidxid', 'splevel', 'dplevel', 'spclass', 'dpclass', 'time')
class SongAdmin(admin.ModelAdmin):
	list_display = ('songtitle', 'songtype', 'songlevel')

class BoardAdmin(admin.ModelAdmin):
	list_display = ('title',)
class BoardCommentAdmin(admin.ModelAdmin):
	list_display = ('writer', 'ip', 'get_boardtitle', 'text')
	form = BoardCommentForm
class SongCommentAdmin(admin.ModelAdmin):
	list_display = ('writer', 'ip', 'get_songinfo', 'get_ranktableinfo',  'text')

# register
admin.site.register(models.RankTable, RankTableAdmin)
admin.site.register(models.RankCategory, RankCategoryAdmin)
admin.site.register(models.RankItem, RankItemAdmin)
admin.site.register(models.Player, PlayerAdmin)
admin.site.register(models.Song, SongAdmin)
admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardComment, BoardCommentAdmin)
admin.site.register(models.SongComment, SongCommentAdmin)
admin.site.register(models.BannedUser)
