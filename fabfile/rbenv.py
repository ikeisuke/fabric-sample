from fabric.api import env, cd, run, sudo
from fabric.contrib.files import exists
from fabric.decorators import task
import yum

env.rbenv_root = '/opt/rbenv'
env.plugins = {
  'ruby-build': 'https://github.com/sstephenson/ruby-build.git'
}

@task
def install():
  yum.install('git')
  rbenv_root = env.rbenv_root
  if not exists(rbenv_root):
    sudo('git clone https://github.com/sstephenson/rbenv.git %s' % rbenv_root)
  install_plugin('ruby-build')
  sudo('cat /dev/null > /etc/profile.d/rbenv.sh')
  sudo('echo \'export RBENV_ROOT=%s\' >> /etc/profile.d/rbenv.sh' % env.rbenv_root)
  sudo('echo \'export PATH="$RBENV_ROOT/bin:$PATH"\' >> /etc/profile.d/rbenv.sh')
  sudo('echo \'eval "$(rbenv init -)"\' >> /etc/profile.d/rbenv.sh')
  sudo('source /etc/profile.d/rbenv.sh')
  install_ruby('2.1.2')
  sudo('rbenv global 2.1.2')

def install_plugin(name):
  if not env.plugins.has_key(name):
    return
  rbenv_root = env.rbenv_root
  plugin_dir = rbenv_root + '/plugins/' + name
  if not exists(plugin_dir):
    sudo('git clone %s %s' % (env.plugins[name], plugin_dir))

def install_ruby(version):
  yum.install('gcc readline-devel openssl-devel')
  res=run('rbenv versions | grep %s' % version, warn_only=True, quiet=True)
  if not res.succeeded:
    sudo('rbenv install %s' % version)
