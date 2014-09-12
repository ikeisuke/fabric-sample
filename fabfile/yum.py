from fabric.api import cd, run, sudo
from fabric.decorators import task

def install(name):
  sudo('yum install %s -y' % (name))
