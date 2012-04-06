from fabric.api import *
from fabric.contrib.files import *
from path import path as ppath


app = env.app = {
    'repo': ppath('/var/local'),
    'localrepo': ppath('.').abspath().parent,
}


try: from localcfg import *
except: pass


app.update({
    'instance_var': app['repo']/'instance',
    'sandbox': app['repo']/'sandbox',
    'user': 'zope',
})


@task
def ssh():
    open_shell()


@task
def install(force=False):
    if not exists(app['repo']):
        run("git init '%s'" % app['repo'])

    local("git push -f '%(git-remote)s:%(repo)s' HEAD:incoming" % {
        'git-remote': env.host_string,
        'repo': app['repo'],
    })
    with cd(app['repo']):
        if force:
            run("git reset incoming --hard")
        else:
            run("git merge incoming --ff-only")

    if not exists(app['sandbox']):
        run("virtualenv -p python2.6 --no-site-packages '%(sandbox)s'" % app)
        run("echo '*' > '%(sandbox)s/.gitignore'" % app)

    run("%(sandbox)s/bin/pip install -r %(repo)s/requirements.txt" % app)

    if not exists(app['instance_var']):
        run("mkdir -p '%(instance_var)s'" % app)

    upload_template(app['localrepo']/'fabfile'/'production-settings.py',
                    str(app['instance_var']/'settings.py'),
                    context=app, backup=False)

    upload_template(app['localrepo']/'fabfile'/'supervisord.conf',
                    str(app['sandbox']/'supervisord.conf'),
                    context=app, backup=False)


@task
def service(action):
    run("'%(sandbox)s/bin/supervisorctl' %(action)s %(name)s" % {
            'sandbox': app['sandbox'],
            'action': action,
            'name': 'natura2000db',
        })


@task
def deploy():
    execute('install')
    execute('service', 'restart')
