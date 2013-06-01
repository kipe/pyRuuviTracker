pyRuuviTracker
==============

Client library for RuuviTracker in python

Installation
------------
```
git clone git://github.com/kipe/pyRuuviTracker.git
cd pyRuuviTracker
virtualenv .
source bin/activate
python setup.py install
```

To use rt_sim
-------------
```
cd rt_sim
pip install -r requirements.txt
python test_script.py tracker_code shared_secret test.gpx [time divider (for speedup)]
```