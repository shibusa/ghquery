# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import bcrypt
import re

class UserManager(models.Manager):
    def modelreg(self, request):
        error = {}
        if len(request.POST['first']) < 2:
            error["first"] = "Please include a first name longer than two characters."
        if len(request.POST['last']) < 2:
            error["last"] = "Please include a last name longer than two characters."
        if len(request.POST['password']) < 8:
            error["passlength"] = "Passwords must be at least 8 characters."
        if request.POST['password'] != request.POST['confirm']:
            error["passmatch"] = "Passwords must match"
        try:
            self.get(account=request.POST['account'])
        except ObjectDoesNotExist:
            pass
        else:
            error["accounttaken"] = "Account already in use."

        if not len(error):
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
            return (True, create)
        else:
            return (False, error)

    def modellog(self, request):
        try:
            stored = self.get(account=request.POST['account'])
            submitted = request.POST['password']
            if bcrypt.checkpw(submitted.encode(), stored.password.encode()):
                return (True, stored)
        except ObjectDoesNotExist:
            pass
        return (False, {"logmatch": "Matching account/password not found"})

class User(models.Model):
    first = models.CharField(max_length=255)
    last = models.CharField(max_length=255)
    account = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
