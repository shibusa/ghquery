# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from models import QueryModel
import socket

# Import login here
from loginadmin.views import sessioncheck

rootpath = '/'

def index(request):
    if 'user' in request.session:
        context = QueryModel.objects.display(request)
        # For testing loadbalanced django nodes
        context["hostname"] = socket.gethostname()
        return render(request, 'githubquery/index.html', context)
    return redirect(rootpath)

def query(request):
    if 'user' in request.session:
        queryresult = QueryModel.objects.query(request)
        message = "{0} {1}".format(request.POST["githubaccount"], queryresult)
        if queryresult == "found":
            messages.success(request, message)
        elif queryresult == "not found":
            messages.error(request, message)
        elif queryresult == "deactivated":
            messages.info(request, message)
    return redirect(rootpath)

def delete(request, query_id):
    if request.method == "POST":
        print QueryModel.objects.get(id=query_id).delete()
    return redirect(rootpath)
