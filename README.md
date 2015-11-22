iidxranktable
==========

online iidx clear table service for [iidx.me](http://iidx.me) users.

currently running on [AWS](http://54.69.39.175/iidx), or [insane.pe.kr/iidx](http://insane.pe.kr/iidx).


### Environment

Python (django)

~~uWSGI, Redis~~

SQL (MariaDB)


### How to use

run ```pip install -r requirements.txt``` and ```python manage.py runserver```.

To update DB, run 
```
python manage.py shell
from iidxrank.update import updatedb
from iidxrank import models
updatedb.setModel(models)
updatedb.update_iidxme()
updatedb.update_DP()
```
or go into ```/admin``` for admin page. (song information from iidx.me, DP from zasa.sakura.ne.jp)

Read django documentation for more information.


### TODO

calculating user's performance
