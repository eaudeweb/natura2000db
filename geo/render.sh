CMD="/home/vagrant/mapping/bin/tilestache-seed.py -c tilestache-disk.cfg"
BBOX="-b 44 20 49 31"
ZOOMS="1 2 3 4 5 6 7 8 9 10 11 12 13"
$CMD $BBOX -l conservare-scispa $ZOOMS
$CMD $BBOX -l conservare-etc $ZOOMS
$CMD $BBOX -l administrativ $ZOOMS
$CMD $BBOX -l ape $ZOOMS
$CMD $BBOX -l infrastructura $ZOOMS
