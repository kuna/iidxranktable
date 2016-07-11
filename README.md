iidxranktable
==========

online iidx clear table service for [iidx.me](http://iidx.me) users.

currently running on [AWS](http://insane.pe.kr/iidx).


### Environment

Python (django, celery, scipy for difficulty calculation)

SQL (MariaDB)

Redis

### How to use

run ```pip install -r requirements.txt``` and ```python manage.py runserver```.

Easy way to install scipy: install anaconda(win) or python-scipy(apt-get).

To update DB peridically, run these command:
```
celery -A update beat -l info
```

To update DB manually,
```
celery -A update worker -l info
```
This will update song list, user list and clear list, and calculate predicted user/song level.

Use ```/admin``` or rankedit page to modify database easily.

### License

MIT License

This project includes some other project's code: bootstrap, dragula, mooEditable. All copyright reversed.
