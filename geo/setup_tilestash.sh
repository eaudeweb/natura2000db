#!/bin/sh

cd ~
virtualenv mapping
. mapping/bin/activate
pip install tilestache werkzeug modestmaps
deactivate
#cd /natura2000db/geo/
#~/mapping/bin/tilestache-server.py -i 0.0.0.0
