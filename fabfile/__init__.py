from fabric.api import *
from fabric.contrib.files import *
from path import path as ppath


app = env.app = {
    'repo': ppath('/var/local'),
    'localrepo': ppath(__file__).abspath().parent.parent,
}


try: from localcfg import *
except: pass


app.update({
    'instance_var': app['repo']/'instance',
    'sandbox': app['repo']/'sandbox',
    'user': 'zope',
})


@task
def i18n_extract():
    local("pybabel extract --omit-header --mapping=babel.cfg "
          "-o i18n/messages.pot '%(localrepo)s'" % app)

@task
def i18n_init(new_locale):
    local("pybabel init -i '%(localrepo)s'/i18n/messages.pot "
          "-d '%(localrepo)s'/i18n "
          "-l %(new_locale)s" % {
              'localrepo': app['localrepo'],
              'new_locale': new_locale})

@task
def i18n_update():
    local("pybabel update "
          "-i '%(localrepo)s'/i18n/messages.pot "
          "-d '%(localrepo)s'/i18n" % app)

@task
def i18n_compile():
    local("pybabel compile -d '%(localrepo)s'/i18n" % app)


@task
def manual_html():
    local("sphinx-build -b html "
          "-d '%(localrepo)s'/manual/_build/doctrees " # spthinx cache
          "'%(localrepo)s'/manual " # source
          "'%(localrepo)s'/manual/_build/html" # destination
          % app)


@task
def ssh():
    open_shell("cd '%(repo)s'" % app)


def _install_random_key(remote_path, key_length=20, mode=0600):
    import random
    import string
    from StringIO import StringIO
    vocabulary = string.ascii_letters + string.digits
    key = ''.join(random.choice(vocabulary) for c in xrange(key_length))
    put(StringIO(key), remote_path, mode=mode)


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
        run("virtualenv -p python2.6 "
            "--no-site-packages --distribute "
            "'%(sandbox)s'" % app)
        run("echo '*' > '%(sandbox)s/.gitignore'" % app)

    run("%(sandbox)s/bin/pip install -r %(repo)s/requirements.txt" % app)

    if not exists(app['instance_var']):
        run("mkdir -p '%(instance_var)s'" % app)

    secret_key_path = app['instance_var']/'secret_key.txt'
    if not exists(secret_key_path):
        _install_random_key(str(secret_key_path))

    put(app['localrepo']/'fabfile'/'production-settings.py',
        str(app['instance_var']/'settings.py'))

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
    execute('install', force=True)
    execute('service', 'restart')
