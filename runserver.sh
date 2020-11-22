while true; do
  python3 manage.py runserver 1100
  echo -e "------\nServer died. restart in 60 secs.\nTo Stop server, Press ^C.\n------"
  sleep 60
done
