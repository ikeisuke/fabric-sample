from fabric.api import env, cd, run, sudo
from fabric.contrib.files import exists
from fabric.decorators import task
import re

def install():
  sudo('yum install -y gcc openssl-devel')
  if run('which pyenv', warn_only=True, quiet=True).failed:
    sudo('yum install -y python-devel python-setuptools')
  if run('which pip', warn_only=True, quiet=True).failed:
    sudo('easy_install pip')
  python_version = run('python -V')
  if re.match(r'^Python 2\.6\.', python_version) is None:
    sudo('pip install fabric paramiko')
  else:
    sudo('pip install fabric paramiko==1.13')
  sudo('pyenv rehash', warn_only=True, quiet=True)
