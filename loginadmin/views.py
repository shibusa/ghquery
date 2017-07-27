# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render,redirect
from django.contrib import messages
from models import User
import socket

requestpath = '/'
newhome = '/githubquery'

def session(request, user):
    request.session['user'] = {
        'id' : user.id,
        'first' : user.first,
        'last' : user.last,
        'account' : user.account
    }
    return redirect(requestpath)

def sessioncheck(request, action=None):
    if 'user' in request.session:
        if request.path == requestpath:
            return redirect(newhome)
        elif request.path == requestpath + "admin/" and User.objects.get(account=request.session['user']['account']).admin:
            context = {"users": User.objects.values('id', 'first', 'last', 'account', 'admin', 'updated_at')}
            return render(request, 'loginadmin/admin.html', context)
        elif request.path == requestpath + "logout":
            request.session.pop('user')
        else:
            return action
    else:
        if request.path == requestpath:
            # For testing loadbalanced django nodes
            context = {"hostname": socket.gethostname()}
            return render(request, 'loginadmin/index.html', context)
        # DO NOT USE IN PRODUCTION, exposes admin console:
        elif request.path == requestpath + "admin/":
            context = {"users": User.objects.values('id', 'first', 'last', 'account', 'admin', 'updated_at')}
            return render(request, 'loginadmin/admin.html', context)
    return redirect(requestpath)

def index(request):
    return sessioncheck(request)

def admin(request):
    return sessioncheck(request)

def logout(request):
	return sessioncheck(request)

def register(request):
    if request.method == "POST":
        result = User.objects.modelreg(request)
        if result[0] == True:
            messages.success(request, "{} created".format(result[1].account))
        else:
            for error in result[1]:
                messages.error(request, result[1][error], extra_tags=error)
    return redirect(requestpath + 'admin/')

def login(request):
    if request.method == "POST":
        result = User.objects.modellog(request)
        if result[0] == True:
            return session(request, result[1])
        else:
            for error in result[1]:
                messages.error(request, result[1][error], extra_tags=error)
    return redirect(requestpath)
