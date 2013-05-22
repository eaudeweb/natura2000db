Natura2000 database
===================

http://biodiversitate.mmediu.ro/rio/natura2000

A database and search interface for natura2000 sites in Romania. For
every protected area the database contains a document with a complex
schema, that is indexed in Solr. The database can be searched via a
faceted search interface through the web app.

The website also contains an interactive map with point and polygon
editor, for use by environment experts, to mark industrial and other
man-made sites within a protected area.


Requirements
============
The application is implemented in Flask, with Backbone on the front-end,
with solr acting as index and also primary data store. It runs on any
Unix-like or Windows OS with Python 2.6 or 2.7 and Java 1.5 for Solr.


Map workflow
============

http://biodiversitate.mmediu.ro/rio/natura2000/map/

The map displays several layers :SCIs and SPAs and other protected areas
by default; administrative borders, water bodies, and infrastructure can
be turned on. Clicking on the map shows information about the features
at those coordinates in a box in the top-right corner of the map. There
is also a measurement functionality (distances and areas) at the
top part of the left-side menu. The base layer can be switched between
OpenStreetMap, Bing maps, and Google maps.

There is an additional editable layer that is tied to the
user's gmail account if they log in. Users can create points and
polygons by entering coordinates in the Stereo70 projection. For
instance, lng=500000 lat=500000 is near the center of Romania. A user
must explicitly save the layer (from the cog-wheel menu next to the
point/polygon creation functions) for it to be persisted.


Setup
=====

1. Install Python >= 2.6 and virtualenv; activate the virtualenv::

    virtualenv -p python2.6 sandbox
    echo '*' > sandbox/.gitignore
    . sandbox/bin/activate

2. Install dependencies::

    pip install -r requirements-dev.txt

3. Optionally create a local configuration file::

    mkdir instance
    echo "DEBUG = True" > instance/settings.py

4. Run the server::

    ./manage.py runserver


Solr database
=============

Documents are stored and indexed in a Solr database. Solr is installed
separately but the configuration is provided in the ``solr`` directory.

1. Download Solr somewhere outside the project repository::

    curl -O http://www.eu.apache.org/dist/lucene/solr/3.5.0/apache-solr-3.5.0.tgz
    tar xzf apache-solr-3.5.0.tgz

2. Start Solr with our configuration. Assuming __solrkit__ is the
   ``apache-solr-3.5.0`` folder unpacked above, and __repo__ is the
   project repository, run::

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

To run the application with Zope, first start Solr, then the `manage.py`
server, and then zope (by running ``bin/zope-instance fg`` from within
the ``buildout`` directory). The application should be accessible at
``http://localhost:8080/chm_ro/rio/natura2000/``.


Loading data from Access database
=================================

1. Dump documents to json. This assumes the Access database is loaded in
   MySQL on `localhost`, in the database `rio`::

    pip install -r migrations/requrements.txt
    ./manage.py accessdb_mjson > instance/access.mjson

2. Load json to Solr::

    ./manage.py import_mjson < instance/access.mjson
