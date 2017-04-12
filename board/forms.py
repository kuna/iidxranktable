#-*- coding: utf-8 -*-
from django import forms
from captcha.fields import ReCaptchaField
import models


def checkValidText(text):
    for banword in models.BannedWord.objects.all():
        if banword.word in text:
            return False
    return True


class CommentForm(forms.Form):
    captcha = ReCaptchaField()


class PostForm(forms.Form):
    """
    Posting form class
    """
    captcha = ReCaptchaField()
    mode = forms.CharField(widget=forms.HiddenInput(), initial='add')
    title = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-sm'}))
    writer = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control input-sm'}))
    password = forms.CharField(
            widget=forms.PasswordInput(attrs={'class':'form-control input-sm'}),
            required=False)
    tag = forms.CharField(
            widget=forms.TextInput(attrs={'class':'form-control input-sm'}),
            required=False)
    text = forms.CharField(widget=forms.Textarea(
        attrs={'class':'form-control','rows':4,'cols':5,
            'id':'richedit',
            'placeholder':u'내용을 입력하세요'}
        ))

    def check_valid_modify_or_add(self, ip):
        if (len(self.data['title']) <= 0):
            self.add_error(u"제목이 너무 짧습니다.")
            return False
        if (len(self.data['text']) <= 3 or len(self.data['writer']) <= 0):
            self.add_error(u"코멘트나 이름이 너무 짧습니다.")
            return False
        if (not checkValidText(self.data['text'])):
            self.add_error(u"코멘트에 사용할 수 없는 단어/태그가 들어가 있습니다.")
            return False
        if (models.BannedUser.objects.filter(ip=ip).count()):
            self.add_error(u"차단당한 유저IP입니다.")
            return False
        return True

    def is_valid_with_ip(self, ip, attr=0, password=None):
        mode = self.data["mode"]
        if (mode != "delete" and not self.is_valid()):
            return False

        if (mode == "delete"):
            password = self.data["password"]
            if (self.data['password'] != password and 'attr' != 2):
                self.add_error(u"Cannot delete post.")
                return False
        elif (mode == "modify"):
            if (not self.check_valid_modify_or_add(ip)):
                return False
            password = self.data["password"]
            if (self.data['password'] != password and 'attr' != 2):
                self.add_error(u"Cannot modify post.")
                return False
        elif (mode == "add"):
            if (not self.check_valid_modify_or_add(ip)):
                return False
        else:
            self.add_error(u"Invalid action parameter given. something wrong happened.")
            return False

        return True
