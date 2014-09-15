from fabric.api import env, cd, run, sudo
from fabric.contrib.files import exists
from fabric.decorators import task
import yum

env.nvm_root = '/opt/nvm'

def install():
  yum.install('git')
  if not exists(env.nvm_root):
    sudo('git clone https://github.com/creationix/nvm.git %s' % env.nvm_root)
  with cd(env.nvm_root):
   sudo('git checkout `git describe --abbrev=0 --tags`') 
  sudo('cat /dev/null > /etc/profile.d/nvm.sh')
  sudo('echo \'source %s/nvm.sh\' >> /etc/profile.d/nvm.sh' % env.nvm_root)
  sudo('source /etc/profile.d/nvm.sh')
  install_nodejs('0.10')
  use('0.10')

def install_nodejs(version):
  yum.install('gcc gcc-c++ openssl-devel')
  res=run('nvm ls | grep %s' % version, warn_only=True, quiet=True)
  if not res.succeeded:
    sudo('nvm install %s' % version)

def use(version):
  sudo('nvm use %s' % version)
