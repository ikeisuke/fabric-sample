# -*- coding: utf-8 -*-
from fabric.api import env, cd, run, sudo, put
from fabric.contrib.files import exists, sed, upload_template
from fabric.decorators import task
import yum
import rbenv

'''
nginx公式rpmの設定
nginx version: nginx/1.6.1
built by gcc 4.8.2 20140120 (Red Hat 4.8.2-16) (GCC)
TLS SNI support enabled
configure arguments: --prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-http_ssl_module --with-http_realip_module --with-http_addition_module --with-http_sub_module --with-http_dav_module --with-http_flv_module --with-http_mp4_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_random_index_module --with-http_secure_link_module --with-http_stub_status_module --with-http_auth_request_module --with-mail --with-mail_ssl_module --with-file-aio --with-ipv6 --with-http_spdy_module --with-cc-opt='-O2 -g -pipe -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic'

必要なさそうなモジュールを削除
--prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-http_realip_module --with-http_gunzip_module --with-http_gzip_static_module --with-http_stub_status_module --with-file-aio --with-cc-opt='-O2 -g -pipe -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic'

passenger有効時付与される
--prefix=/etc/nginx --with-http_ssl_module --with-http_gzip_static_module --with-http_stub_status_module
'''
env.nginx_build_option = "--prefix=/etc/nginx --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --lock-path=/var/run/nginx.lock --http-client-body-temp-path=/var/cache/nginx/client_temp --http-proxy-temp-path=/var/cache/nginx/proxy_temp --http-fastcgi-temp-path=/var/cache/nginx/fastcgi_temp --http-uwsgi-temp-path=/var/cache/nginx/uwsgi_temp --http-scgi-temp-path=/var/cache/nginx/scgi_temp --user=nginx --group=nginx --with-http_ssl_module --with-http_gzip_static_module --with-http_stub_status_module --with-http_realip_module --with-http_gunzip_module --with-file-aio --with-cc-opt='-O2 -g -pipe -Wno-error -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m64 -mtune=generic'"
env.src_dir = '/usr/local/src'

def install(version = '1.6.1'):
  yum.install('wget gcc pcre-devel zlib-devel')
  with cd(env.src_dir):
    _setup_source(version)
    with cd('nginx-%s' % version):
      sudo('./configure %s' % env.nginx_build_option)
      sudo('make')
      sudo('make install')
    _cleanup_source(version)
  _setup_config
  _setup_init_script

def install_with_passenger(nginx = '1.6.1', passenger = '4.0.50'):
  rbenv.install
  sudo('gem install rack --no-document')
  yum.install('wget curl-devel gcc gcc-c++ openssl-devel pcre-devel zlib-devel')
  with cd(env.src_dir):
    _setup_source(nginx)
    if not exists('passenger-%s.tar.gz' % passenger):
      sudo('wget http://s3.amazonaws.com/phusion-passenger/releases/passenger-%s.tar.gz' % passenger)
    if not exists('passenger-%s' % passenger):
      sudo('tar zxfv passenger-%s.tar.gz' % passenger)
    if exists('/opt/passenger-%s' % passenger):
      sudo('rm -rf /opt/passenger-%s' % passenger)
    sudo('mv passenger-%s /opt/' % passenger)
    with cd('/opt/passenger-%s' % passenger):
      sudo('./bin/passenger-install-nginx-module --auto --prefix=/etc/nginx --nginx-source-dir=%s/nginx-%s  --languages=ruby,python,nodejs --extra-configure-flags="%s"' % (env.src_dir, nginx, env.nginx_build_option))
    _cleanup_source(nginx)
  _setup_config
  ruby_version = sudo('rbenv version-name') 
  sed('/etc/nginx/nginx.conf',
      '(^    access_log .*$)',
      '\\1\\n\\n    passenger_root /opt/passenger-%s;\\n    passenger_ruby /opt/rbenv/versions/%s/bin/ruby;' % (passenger, ruby_version),
      use_sudo = True,
      backup = None
  )
  _setup_init_script
 
def _setup_source(version):
  if not exists('nginx-%s.tar.gz' % version):
    sudo('wget http://nginx.org/download/nginx-%s.tar.gz' % version)
  if exists('nginx-%s' % version):
    sudo('rm -rf nginx-%s' % version)
  sudo('tar zxfv nginx-%s.tar.gz' % version)

def _cleanup_source(version):
  if exists('nginx-%s' % version):
    sudo('rm -rf nginx-%s' % version)

def _setup_config():
  sed('/etc/nginx/nginx.conf',
      'worker_processes  .*;',
      'worker_processes  auto;',
      use_sudo = True,
      backup = None
  )

def _setup_init_script():
  upload_template(
    'templates/nginx/redhat.init',
    '/etc/init.d/nginx',
    use_sudo = True,
    backup = None
  )
  sudo('chmod 755 /etc/init.d/nginx')
  sudo('chkconfig --add nginx')
  sudo('chkconfig nginx on')
  sudo('service nginx start')

def test():
  print 'test'
