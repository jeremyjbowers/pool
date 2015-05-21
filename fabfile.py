import datetime
import json
import os

from fabric import api, operations, contrib
from fabric.state import env

PROJECT_NAME = 'pool'
ENVIRONMENTS = {
    "prd": {
        "hosts": ['whitehousepool.org'],
    }
}

env.user = "ubuntu"
env.forward_agent = True
env.branch = "master"

env.hosts = ['127.0.0.1']
env.settings = None

@api.task
def development():
    """
    Work on development branch.
    """
    env.branch = 'development'

@api.task
def master():
    """
    Work on stable branch.
    """
    env.branch = 'master'

@api.task
def branch(branch_name):
    """
    Work on any specified branch.
    """
    env.branch = branch_name

@api.task
def e(environment):
    env.settings = environment
    env.hosts = ENVIRONMENTS[environment]['hosts']

@api.task
def clone():
    api.run('git clone git@github.com:jeremyjbowers/pool.git /home/ubuntu/apps/%s' % PROJECT_NAME)

@api.task
def make_virtualenv():
    api.run('mkvirtualenv pool')

@api.task
def wsgi():
    api.run('touch /home/ubuntu/apps/%s/config/%s/app.py' % (PROJECT_NAME, env.settings))

@api.task
def pull():
    api.run('cd /home/ubuntu/apps/%s; git fetch' % PROJECT_NAME)
    api.run('cd /home/ubuntu/apps/%s; git pull origin %s' % (PROJECT_NAME, env.branch))

@api.task
def pip_install():
    api.run('workon %s && cd /home/ubuntu/apps/%s && pip install -r requirements.txt' % (PROJECT_NAME, PROJECT_NAME))

@api.task
def migrate():
    api.run('workon %s && django-admin migrate' % PROJECT_NAME)

@api.task
def collectstatic():
    api.run('workon %s && django-admin collectstatic --noinput' % PROJECT_NAME)

@api.task
def deploy():
    pull()
    pip_install()
    migrate()
    collectstatic()
    wsgi()

@api.task
def mgmt(management_command):
    api.run('workon %s && django-admin %s' % (PROJECT_NAME, management_command))

@api.task
def snapshot():
    dumpdb()
    getdb()
    loaddb()

@api.task
def dumpdb():
    api.run('pg_dump -U pool -h %s -p 5432 -d pool > /mnt/space/tmp/pool-snapshot.sql' % env.dbs[0])
    api.run('gzip /mnt/space/tmp/pool-snapshot.sql')

@api.task
def getdb():
    operations.get(remote_path="/mnt/space/tmp/pool-snapshot.sql.gz", local_path="/tmp/pool-snapshot.sql.gz")

@api.task
def loaddb():
    api.local('gunzip /tmp/pool-snapshot.sql.gz')
    if os.path.isfile('/tmp/pool-snapshot.sql'):
        api.local('dropdb pool')
        api.local('createdb pool')
        api.local('psql pool < /tmp/pool-snapshot.sql')