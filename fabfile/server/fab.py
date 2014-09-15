from fabric.decorators import task

import pyenv
import tools

@task
def setup():
  pyenv.install()
  tools.fab.install()
