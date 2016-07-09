# https://docs.djangoproject.com/en/1.9/intro/tutorial02/

from django.contrib import admin
from django import forms
import models

class BoardCommentForm(forms.ModelForm):
	class Meta:
		model = models.BoardComment
		fields = '__all__'
		widgets = {
			'text': forms.Textarea(attrs={'cols': 80, 'rows': 20}),
		}


class BoardAdmin(admin.ModelAdmin):
	list_display = ('title',)
class BoardPostAdmin(admin.ModelAdmin):
	list_display = ('writer', 'ip', 'get_boardtitle', 'title', 'tag')
class BoardCommentAdmin(admin.ModelAdmin):
	list_display = ('writer', 'ip', 'get_posttitle', 'text', 'tag')
	form = BoardCommentForm

# register
admin.site.register(models.Board, BoardAdmin)
admin.site.register(models.BoardPost, BoardPostAdmin)
admin.site.register(models.BoardComment, BoardCommentAdmin)
admin.site.register(models.BannedUser)
admin.site.register(models.BannedWord)
