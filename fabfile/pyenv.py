from fabric.api import env, cd, run, sudo
from fabric.contrib.files import exists
from fabric.decorators import task
import yum

env.pyenv_root = '/opt/pyenv'

@task
def install():
  yum.install('git')
  pyenv_root = env.pyenv_root
  if not exists(pyenv_root):
    sudo('git clone https://github.com/yyuu/pyenv.git %s' % pyenv_root)
  sudo('cat /dev/null > /etc/profile.d/pyenv.sh')
  sudo('echo \'export PYENV_ROOT=%s\' >> /etc/profile.d/pyenv.sh' % env.pyenv_root)
  sudo('echo \'export PATH="$PYENV_ROOT/bin:$PATH"\' >> /etc/profile.d/pyenv.sh')
  sudo('echo \'eval "$(pyenv init -)"\' >> /etc/profile.d/pyenv.sh')
  sudo('source /etc/profile.d/pyenv.sh')
  install_python('2.7.8')
  sudo('pyenv global 2.7.8')

def install_python(version):
  yum.install('gcc readline-devel openssl-devel bzip2-devel sqlite-devel')
  res=run('pyenv versions | grep %s' % version, warn_only=True, quiet=True)
  if not res.succeeded:
    sudo('pyenv install %s' % version)
