import os, sys
sys.path.append(os.getcwd() + '/fabfile')

from fabric.api import env
from fabric.decorators import task

env.disable_known_hosts = True
env.connection_attempts = 5
env.timeout             = 60

@task
def version():
  print("0.0.1-beta")

import rbenv
import pyenv
import nvm
import nginx
import gce

import tools
import server
