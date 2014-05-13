github2jenkins
==============

Create Jenkins jobs per Github repository

(c) myGrid, University of Manchester 2014


This script will go through the configured Github users and create a 
Jenkins job for each repository, unless one already exists.

The repository names are assumed to be unique across the specified users.

A pre-existing Jenkins Github job (typically made in the Jenkins web
interface) must be specified as a template. Naive search-replace
customize its configuration per repository (e.g. replacing the github URLs)

Several branches can be specified, in which case a job per branch is
created.

# Dependencies

 * [Python](http://www.python.org/) 2.6 or later
 * [github3.py](https://pypi.python.org/pypi/github3.py/0.1)
 * [jenkinsapi](https://github3py.readthedocs.org/)
 
Installation:

    sudo pip install github3.py
    sudo pip install jenkinsapi

TODO: Make github2jenkins installable with pip

# Configuration


This script has partial configuration as global variables at its top. 
You need to edit the script to configure your repositories
and Jenkins server.

TODO: Move all configuration to ~/.github2jenkins

The script will assume the current Unix username unless {{JENKIS_USER}}
has been set.

The script will ask interactively for the Jenkins password unless
the environment variable {{JENKINS_PASSWORD}} has been set.

