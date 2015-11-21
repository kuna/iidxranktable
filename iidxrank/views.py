from django.http import HttpResponse

#
# -*- encode: utf8 -*-

def test(request):
    return HttpResponse('test')
