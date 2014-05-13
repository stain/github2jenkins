github2jenkins
==============

Create Jenkins jobs per Github repository

(c) [myGrid](http://www.mygrid.org.uk/), University of Manchester 2014


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
 * [pip](http://www.pip-installer.org/)
 * [github3.py](https://pypi.python.org/pypi/github3.py/0.1)
 * [jenkinsapi](https://github3py.readthedocs.org/)
 * A Jenkins instance
 
Installation:

    sudo pip install github3.py
    sudo pip install jenkinsapi

TODO: Make github2jenkins installable with pip

# Example usage

    stain@biggie-mint ~/src/github2jenkins $ python github2jenkins.py
    Github user stain, password [empty: read-only]: 
    Jenkins: http://build.mygrid.org.uk/ci/
    Password for user stain [empty: read-only]: 
    - taverna-activity-test-utils
    - taverna-apiconsumer-activity
    - taverna-apiconsumer-activity-ui
    + taverna-baclava-utilities
    - taverna-beanshell-activity
    + taverna-beanshell-activity-ui
    - taverna-biomart-activity
    - taverna-biomart-activity-ui

This indicates that Jenkins jobs `taverna-baclava-utilities` and 
`taverna-beanshell-activity-ui` was created. The remaining jobs
correspond to the GitHub repositories, but already exist (e.g.
because the script was run earlier).

The Github password is only needed once, as an OAuth token
is stored in `~/github2jenkins`. The default permissions for
this (`GITHUB_SCOPES`) is read-only anonymous access and
so is not particularly sensitive.


# Configuration

TODO: Move all configuration to `~/.github2jenkins`

This script is configured by editing the global variables.

You need to edit the script to configure your repositories
and Jenkins server:

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



The script will assume the current Unix username unless `JENKIS_USER`
has been set.

The script will ask interactively for the Jenkins password unless
the environment variable `JENKINS_PASSWORD` has been set.

