from oauth2client import gce
from fabric.api import env
from fabric.decorators import task
import httplib2

@task
def auth():
  credentials = gce.AppAssertionCredentials(
    scope='https://www.googleapis.com/auth/compute')
  http = credentials.authorize(httplib2.Http())

@task
def project(project):
  env.gce_project = project

