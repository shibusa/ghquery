# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.contrib import messages
from models import User
from githubquery.models import QueryModel

requestpath = '/'
newhome = '/githubquery/'

def index(request):
    if 'user' in request.session:
        return redirect(newhome)
    return render(request, 'loginadmin/index.html')

def admin(request):
    if 'user' in request.session and User.objects.get(account=request.session['user']['account']).admin:
        return render(request, 'loginadmin/admin.html', User.objects.displaydata())
    return redirect(requestpath)

def logout(request):
    if 'user' in request.session:
        request.session.pop('user')
    return redirect(requestpath)

def register(request):
    if 'user' in request.session and request.method == "POST":
        User.objects.modelreg(request)
    return redirect(requestpath + 'admin/')

def login(request):
    if request.method == "POST":
        User.objects.modellog(request)
    return redirect(requestpath)

def deleteuser(request, query_id):
    if 'user' in request.session and User.objects.get(account=request.session['user']['account']).admin:
        if query_id != 1:
            User.objects.get(id=query_id).delete()
            QueryModel.objects.filter(userid=query_id).delete()
    return redirect(requestpath + 'admin/')
