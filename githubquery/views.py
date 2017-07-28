# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from models import QueryModel
import socket

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
        QueryModel.objects.query(request)
    return redirect(rootpath)

def delete(request, query_id):
    if 'user' in request.session:
        query = QueryModel.objects.get(id=query_id)
        if query.userid.id == request.session['user']['id']:
            query.delete()
    return redirect(rootpath)
