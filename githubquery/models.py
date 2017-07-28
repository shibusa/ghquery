# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from loginadmin.models import User
import requests

class GithubUserManager(models.Manager):
    def githubuser(self, ghacct):
        # Check if github user exists
        statuscode = requests.head("https://api.github.com/users/{}/repos".format(ghacct)).status_code
        if statuscode == 200:
            # See if github user has been added to database
            try:
                return ("found", self.get(githubuser=ghacct))
            # Create entry in database for github user
            except ObjectDoesNotExist:
                return ("found", self.create(githubuser=ghacct))
        else:
            # Deactivate user and all repos if user was added to database, but no longer exists
            if self.filter(githubuser=ghacct).exists():
                userupdate = self.get(githubuser=ghacct).update(deactivated=True)
                RepoModel.objects.filter(githubuserid=userupdate).update(removed=True)
                return ("deactivated")
            return ("not found")

class RepoManager(models.Manager):
    def addrepos(self, ghuser, repolist):
        for repo in repolist:
            if repo["description"]:
                self.create(githubuserid=ghuser, reponame=repo["name"], repourl=repo["html_url"], repodescription=repo["description"])
            else:
                self.create(githubuserid=ghuser, reponame=repo["name"], repourl=repo["html_url"])

    def disablerepos(self, query, repolist):
        query.filter(reponame__in=repolist).update(removed=True)

    def repo(self, ghuser):
        # Obtain repo JSON
        apiresponse = requests.get("https://api.github.com/users/{}/repos".format(ghuser.githubuser)).json()
        # Compares existing repos in database with those obtained from reponse
        userquery = self.filter(githubuserid=ghuser)
        apiresponserepos = set([repo["name"] for repo in apiresponse])
        userqueryrepos = set([repo.reponame for repo in userquery])
        newrepos = apiresponserepos.difference(userqueryrepos)
        oldrepos = userqueryrepos.difference(apiresponserepos)

        # Strip apiresponselist to only new repos
        apiresponse = [repodetails for repodetails in apiresponse if repodetails["name"] in newrepos]
        self.addrepos(ghuser, apiresponse)
        self.disablerepos(userquery, oldrepos)

class QueryManager(models.Manager):
    def query(self, request):
        ghacct = request.POST['githubaccount']
        appuser = User.objects.get(id=request.session['user']['id'])
        # Ensure github user is in database
        ghuser = GithubUserModel.objects.githubuser(request.POST['githubaccount'])
        # Create query if user is found in GithubUserModel
        message = "{0} {1}".format(request.POST["githubaccount"], ghuser[0])
        if ghuser[0] != "notfound":
            RepoModel.objects.repo(ghuser[1])
            self.create(userid=appuser,githubuserid=ghuser[1])
            if ghuser[0] == "deactivated":
                messages.info(request, message)
            else:
                messages.success(request, message)
        else:
            messages.error(request, message)

    def displayself(self, appuser):
        queries = self.filter(userid=appuser['id']).prefetch_related('userid', 'githubuserid').order_by('-created_at')
        ghusers = set([item.githubuserid_id for item in queries])
        repos = RepoModel.objects.filter(githubuserid__in=ghusers)
        return {"queries": queries, "repos": repos}

    def displayothers(self, appuser):
        queries = self.exclude(userid=appuser['id']).prefetch_related('userid', 'githubuserid').order_by('-created_at')
        ghusers = set([item.githubuserid_id for item in queries])
        repos = RepoModel.objects.filter(githubuserid__in=ghusers)
        return {"queries": queries, "repos": repos}

    def display(self, request):
        currentuser = request.session['user']
        return {"self": self.displayself(currentuser), "others": self.displayothers(currentuser)}

class GithubUserModel(models.Model):
    githubuser = models.CharField(max_length=255, unique=True)
    deactivated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = GithubUserManager()

class RepoModel(models.Model):
    githubuserid = models.ForeignKey(GithubUserModel)
    reponame = models.CharField(max_length=255)
    repourl = models.CharField(max_length=255)
    repodescription = models.CharField(max_length=255, blank=True)
    removed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = RepoManager()

class QueryModel(models.Model):
    userid = models.ForeignKey(User)
    githubuserid = models.ForeignKey(GithubUserModel)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QueryManager()
