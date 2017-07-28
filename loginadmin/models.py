# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import bcrypt
import re

class UserManager(models.Manager):
    def displaydata(self):
        contextdict = {"users": User.objects.values('id', 'first', 'last', 'account', 'admin', 'updated_at')}
        return contextdict

    def validate_reg(self, request):
        errordict = {}
        if len(request.POST['first']) < 2:
            errordict["first"] = "Please include a first name longer than two characters."
        if len(request.POST['last']) < 2:
            errordict["last"] = "Please include a last name longer than two characters."
        if len(request.POST['password']) < 8:
            errordict["passlength"] = "Passwords must be at least 8 characters."
        if request.POST['password'] != request.POST['confirm']:
            errordict["passmatch"] = "Passwords must match"
        try:
            self.get(account=request.POST['account'])
        except ObjectDoesNotExist:
            pass
        else:
            error["accounttaken"] = "Account already in use."
        return errordict

    def modelreg(self, request):
        errors = self.validate_reg(request)
        if not len(errors):
            # Change checkbox value to boolean
            if 'admin' in request.POST and request.POST['admin'] == "on":
                adminbox = True
            else:
                adminbox = False

            passwordhash = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
            create = self.create(
                first=request.POST['first'],
                last=request.POST['last'],
                account=request.POST['account'],
                password=passwordhash,
                admin=adminbox
            )
            messages.success(request, "{} created".format(create.account))
        else:
            for errortype, errormsg in errors.iteritems():
                messages.error(request, errormsg, extra_tags=errortype)

    def modellog(self, request):
        try:
            stored = self.get(account=request.POST['account'])
            submitted = request.POST['password']
            if bcrypt.checkpw(submitted.encode(), stored.password.encode()):
                request.session['user'] = {
                    'id' : stored.id,
                    'first' : stored.first,
                    'last' : stored.last,
                    'account' : stored.account
                }
            return
        except ObjectDoesNotExist:
            pass
        messages.error(request, "Matching account/password not found", extra_tags="logmatch")

class User(models.Model):
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)
    account = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
