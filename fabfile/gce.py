from fabric.api import env, local, settings
from fabric.decorators import task
import uuid

env.gce_project = open('.gce_default_project').read().strip()
env.gce_zone    = open('.gce_default_zone').read().strip()

@task
def auth():
  install()
  with settings(warn_only=True, quiet=True):
    if local('gcloud auth list  | grep active').succeeded:
      return
  local('gcloud auth login --no-launch-browser --project=%s --quiet' % env.gce_project)

@task
def install():
  with settings(warn_only=True, quiet=True):
    if local('which gcloud').succeeded:
      return
  local('curl https://sdk.cloud.google.com | sudo bash')
  

@task
def project(project):
  env.gce_project = project

@task
def zone(zone):
  env.gce_zone = zone

@task
def create_instance(machine_type = 'n1-highcpu-2'):
  auth()
  instance_id = uuid.uuid4()
  sshkeys     = open('.gce_server_pubkeys').read().strip()
  result = local('gcloud compute instances create i-%s --project=%s --zone=%s --machine-type=%s --boot-disk-type=pd-ssd --image=https://www.googleapis.com/compute/v1/projects/centos-cloud/global/images/centos-6-v20140718  --metadata="sshKeys=%s"' % (instance_id, env.gce_project, env.gce_zone, machine_type, sshkeys), capture=True)
  env.hosts = [result.split("\n")[1].split(' ')[4]]
  print(result)
