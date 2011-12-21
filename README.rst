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

    APP_SETTINGS=$DATA/config.py python demo.py runserver

6. Optionally create a script in __venv__/bin/rio to simplify the above
   command (__venv__ stands for the path to the virtualenv folder).
   Don't forget to make it executable (``chmod +x __venv__/bin/rio``)::

    #!/bin/bash
    PRJ='__venv__'
    export APP_SETTINGS=$PRJ/data/config.py
    exec $PRJ/sandbox/bin/python $PRJ/demo.py $@

   Run the script as ``rio runserver``.

7. TODO dump access db to json

8. TODO set up solr config

9. TODO load json to solr
