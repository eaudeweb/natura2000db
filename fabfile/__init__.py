from fabric.api import *
from fabric.contrib.files import exists


app = env.app = {
    'repo': '/var/local',
}


try: from localcfg import *
except: pass


app.update({
    'var': '%(repo)s/instance' % app,
    'sandbox': '%(repo)s/sandbox' % app,
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

    instance = '%(repo)s/instance' % app
    if not exists(instance):
        run("mkdir -p '%s'" % instance)
