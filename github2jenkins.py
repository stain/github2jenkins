#!/usr/bin/env python

"""
Create Jenkins job corresponding to each Github repository.
"""

import sys
import os
import getpass
from ConfigParser import ConfigParser
import github3
import jenkinsapi


# Github user(s) which repositories are to be created in Jenkins
# Needed to avoid rate limits of 60 request/hour
GITHUB_USERS = ["taverna"]

# Github username for authentication
GITHUB_AUTH_USER = os.environ.get("JENKINS_USER") or getpass.getuser()

# Scope of Github API access
# []                # public read-only
# ["repo", "user"]  # private repos
GITHUB_SCOPES = []

# Branches which existance means a corresponding Jenkins job is
# created. The job will be called $repository-$branch, except for 
# the master branch, which is simply $repository
BRANCHES = ["master", "maintenance"]

# Jenkins instance where jobs will be created, e.g.
# http://localhost:8080/jenkins/
JENKINS = "http://build.mygrid.org.uk/ci/"

# Pre-existing Jenkins job which config is
# to be used as a template for any new jobs
# 
# Note: The template must be both a valid 
# Jenkins name and a Github repository
# as naive search-replace is used on the
# Jenkins Job Config XML
# The string "master" will be search-replaced for
# other branches
JENKINS_JOB_TEMPLATE = "-taverna-template-job-"
# The pre-configured user/repo substring of the github URLs in the
# Jenkins job-template - this will be search-replaced to
# $user/$repo
JENKINS_JOB_TEMPLATE_REPO = "taverna/-taverna-template-job-"

class Github2JenkinsException(Exception):
    pass 


_readonly = False


_jenkins = None
def jenkins():
    global _readonly
    global _jenkins
    if _jenkins is not None:
        return _jenkins
    if config().has_section("jenkins"):
        url = config().get("jenkins", "url")
        user = config().get("jenkins", "user")
        password = config().get("jenkins", "password")
    else: 
        url = JENKINS
        user = os.environ.get("JENKINS_USER") or getpass.getuser()
        password = os.environ.get("JENKINS_PASSWORD")
        if user and not password:
            # Need to ask for password    
            print "Jenkins:", JENKINS
            password = getpass.getpass("Password for user " + user +
                                       " [empty: read-only]: ")
            if password:
                if not config().has_section("jenkins"):
                    config().add_section("jenkins")
                config().set("jenkins", "user", user)
                config().set("jenkins", "password", password)
                config().set("jenkins", "url", url)

    if not password: 
        _jenkins = jenkinsapi.jenkins.Jenkins(url)
        _readonly = True
    else:
        _jenkins = jenkinsapi.jenkins.Jenkins(url, user, password)
    return _jenkins    

def repos(username, must_have_branch):
   for repo in github().iter_user_repos(username):
       if repo.branch(must_have_branch):
            yield repo

def _configpath():
    configpath = os.path.expanduser("~/.github2jenkins")
    if not os.path.exists(configpath):
        open(configpath, "w").close()
        os.chmod(configpath, 0600)
    return configpath

_config = None
def config():
    global _config
    if _config is not None:
        return _config
    _config = ConfigParser()        
    _config.read(_configpath())
    return _config

def save_config():
    fp = open(_configpath(), "w")
    try:
        config().write(fp)
    finally:
        fp.close()


_github = None
def github():
    global _github
    # Have we made one earlier today?
    if _github is not None:
        return _github

    # See if we have a token
    _github = _github_w_token()
    if _github is not None:
        return _github

    password = getpass.getpass("Github user {0}, password [empty: read-only]: ".format(GITHUB_AUTH_USER))
    if not password:
        _github = github3.GitHub() # anonymous
        return _github

    # Create OAuth token
    note = "github2jenkins" 
    note_url = "https://github.com/stain/github2jenkins"
    auth = github3.authorize(GITHUB_AUTH_USER, password, GITHUB_SCOPES, note, note_url)
    print auth
    print auth.token
    print auth.id
    if not config().has_section("github"):
        config().add_section("github")
    config().set("github", "token", auth.token)
    config().set("github", "id", auth.id)
    save_config()
    return _github_w_token() 
    
def _github_w_token():
    if not config().has_section("github"):
        return None
    token = config().get("github", "token")
    # Do we need the id for anything?
    #github_id = config().get("github", "id")
    return github3.login(token=token)

_jenkins_template = None
def jenkins_job_template():
    global _jenkins_template
    if _jenkins_template is not None:
        return _jenkins_template

    _jenkins_template_job = jenkins()[JENKINS_JOB_TEMPLATE]   
    if not _jenkins_template_job:
        raise Github2JenkinsException("Can't find template job " + JENKINS_JOB_TEMPLATE)

    _jenkins_template = _jenkins_template_job.get_config()
    return _jenkins_template
    

def job_config_for(name, repository, branch):
    job = jenkins_job_template()
    job = job.replace(JENKINS_JOB_TEMPLATE_REPO, str(repository))
    # Now done by set_scm_on_job()
    #job = job.replace(JENKINS_JOB_TEMPLATE, repository.name)
    #job = job.replace("master", branch)
    return job

def set_scm_on_job(job, repository, branch):
    job.modify_scm_branch(branch)
    job.modify_scm_url(repository.git_url)

def create_jenkins_job(name, repository, branch):
    if _readonly:
        return
    job_config = job_config_for(name, repository, branch)
    job = jenkins().create_job(name, job_config)
    set_scm_on_job(job, repository, branch)
    job.enable()
    return job

def update_jenkins_job(name, repository, branch):
    if _readonly:
        return
    job = jenkins()[name]
    job_config = job_config_for(name, repository, branch)
    job.update_config(job_config)
    set_scm_on_job(job, repository, branch)
    job.enable()
    return job

def main(args):
    force = "-f" in args or "--force" in args
    writable = not ("-r" in args or "--read-only" in args)
    for user in GITHUB_USERS:
        for branch in BRANCHES:
            for repo in repos(user, branch):
                name = repo.name
                if branch != "master":
                    name += "-maintenance"

                if name in jenkins():
                    if force:
                        writable and update_jenkins_job(name, repo, branch)   
                        print "*", name
                    else:
                        print "-", name

                else:
                    print "+", name
                    writable and create_jenkins_job(name, repo, branch) 
                

if __name__=="__main__": 
    status = main(sys.argv[1:])
    if status:
        sys.exit(status)

