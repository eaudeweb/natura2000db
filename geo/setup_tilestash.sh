#!/bin/sh

cd ~
virtualenv mapping
. mapping/bin/activate
pip install tilestache werkzeug modestmaps
deactivate
#cd /natura2000db/geo/
#~/mapping/bin/tilestache-server.py -i 0.0.0.0
#~/mapping/bin/tilestache-seed.py -c tilestache-disk.cfg -b 44 20 49 31 -l all-sites 1 2 3 4 5 6 7 8 9 10 11 12 13
