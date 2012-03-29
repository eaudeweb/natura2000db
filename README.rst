Setup
=====

1. Install Python >= 2.6 and virtualenv; activate the virtualenv.

2. Install dependencies::

    pip install -r requirements-dev.txt

3. Create a local data directory, make sure it's not committed to the
   repository by mistake. We'll call it ``$DATA``.

4. Optionally create a local configuration file::

    mkdir instance
    echo "DEBUG = True" > instance/settings.py

5. Run the server::

    APP_SETTINGS=$DATA/config.py python rio.py runserver

6. Optionally create a script in __venv__/bin/rio to simplify the above
   command (__venv__ stands for the path to the virtualenv folder).
   Don't forget to make it executable (``chmod +x __venv__/bin/rio``)::

    #!/bin/bash
    PRJ='__venv__'
    export APP_SETTINGS=$PRJ/data/config.py
    exec $PRJ/sandbox/bin/python $PRJ/rio.py $@

   Run the script as ``rio runserver``.


Solr database
=============

Documents are stored and indexed in a Solr database. Solr is installed
separately but the configuration is provided in the ``solr`` directory.

1. Download Solr somewhere outside the project repository::

    curl -O http://www.eu.apache.org/dist/lucene/solr/3.5.0/apache-solr-3.5.0.tgz
    tar xzf apache-solr-3.5.0.tgz

2. Start Solr with our configuration. Assuming __solrkit__ is the
``apache-solr-3.5.0`` folder unpacked above, and __repo__ is the project
repository, run::

    cd __solrkit__/example
    java -Dsolr.solr.home=__repo__/solr -jar start.jar


Setup of a CHM3 portal
======================

A minimal buildout is provided in the ``buildout`` folder. It's mostly
self-contained except for the ``NaayaBundles-CHMEU`` package and the
database file.

Get the ``NaayaBundles-CHMEU`` package::

    mkdir buildout/src
    cd buildout/src
    svn co https://svn.eionet.europa.eu/repositories/Naaya/trunk/eggs/NaayaBundles-CHMEU

In the ``buildout`` directory, bootstrap and run the buildout::

    cp buildout-example.cfg buildout.cfg
    python2.4 bootstrap.py -d
    bin/buildout


Finally, copy the database file (``Data.fs``) to ``var/filestorage/``.

To run the application with Zope, first start Solr, then the `rio.py`
server, and then zope (by running ``bin/zope-instance fg`` from within
the ``buildout`` directory). The application should be accessible at
``http://localhost:8080/chm_ro/rio/natura2000/``.


Loading data from Access database
=================================

1. Dump documents to json. This assumes the Access database is loaded in
   MySQL on `localhost`, in the database `rio`::

    pip install -r migrations/requrements.txt
    rio accessdb_mjson > $DATA/access.mjson

2. Load json to Solr::

    rio import_mjson < $DATA/access.mjson
