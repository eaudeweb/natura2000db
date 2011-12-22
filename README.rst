Setup
=====

1. Install Python >= 2.6 and virtualenv; activate the virtualenv.

2. Install dependencies::

    pip install -r requirements-dev.txt

3. Create a local data directory, make sure it's not committed to the
   repository by mistake. We'll call it ``$DATA``.

4. Optionally create a local configuration file::

    echo "STORAGE_ENGINE = 'solr'" > $DATA/config.py

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

1. Set up solr config (TODO)
   Note: the Solr configuration file needs to have these lines::

    <solrQueryParser defaultOperator="AND"/>

    <field name="regcod" type="string" indexed="true" stored="true" multiValued="true"/>
    <field name="type" type="string" indexed="true" stored="true"/>
    <field name="bio_region" type="string" indexed="true" stored="true" multiValued="true"/>
    <field name="habitat_class" type="string" indexed="true" stored="true" multiValued="true"/>
    <field name="orig" type="string" indexed="false" stored="true"/>

2. Dump documents to json. This assumes the Access database is loaded in
   MySQL on `localhost`, in the database `rio`::

    pip install -r migrations/requrements.txt
    rio accessdb_mjson > $DATA/access.mjson

3. Load json to solr::

    rio import_mjson < $DATA/access.mjson
