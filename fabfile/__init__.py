from fabric.api import env
from fabric.decorators import task

@task
def version():
  print("0.0.1-beta")

import rbenv
import pyenv
