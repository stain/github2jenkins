#!/usr/bin/env python

"""
Create Jenkins job corresponding to each Github repository.
"""

import os
import getpass
import github3
import jenkinsapi

# Github user(s) which repositories are to be created in Jenkins
GITHUB_USERS = ["taverna"]

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
JENKINS_JOB_TEMPLATE = "taverna-wsdl-activity"
# The pre-configured user/repo substring of the github URLs in the
# Jenkins job-template - this will be search-replaced to
# $user/$repo
JENKINS_JOB_TEMPLATE_REPO = "taverna/taverna-wsdl-activity"

# Jenkins user with write-access in Jenkins
# The library will prompt on the console at runtime for
# the jenkins password.
#
# Set the user to None for readonly mode, in  which case
# new Jenkins jobs will not be created, but their name
# printed on the console.
# 
JENKINS_USER = os.environ.get("JENKINS_USER") or getpass.getuser()


class Github2JenkinsException(Exception):
    pass 


gh = github3.GitHub()


_jenkins = None

def jenkins():
    global _jenkins
    if _jenkins is not None:
        return _jenkins

    password = os.environ.get("JENKINS_PASSWORD")
    if JENKINS_USER and not password:
        # Need to ask for password    
        print "Jenkins:", JENKINS
        password = getpass.getpass("Password for user " + JENKINS_USER +
                                   " [empty for read-only]: ")

    if not password: 
        _jenkins = jenkinsapi.jenkins.Jenkins(JENKINS)
    else:
        _jenkins = jenkinsapi.jenkins.Jenkins(JENKINS, JENKINS_USER, password)
    return _jenkins    

def repos(username, must_have_branch):
   for repo in gh.iter_user_repos(username):
       if repo.branch(must_have_branch):
            yield repo


_jenkins_template = None
def create_template(job_name, repository):
    global _jenkins_template
    if _jenkins_template is not None:
        return _jenkins_template
    _jenkins_template = jenkins()[JENKINS_JOB_TEMPLATE]    
    if not _jenkins_template:
        raise Github2JenkinsException("Can't find template " + JENKINS_JOB_TEMPLATE)
    return _jenkins_template


