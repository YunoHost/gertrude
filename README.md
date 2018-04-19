Gertrude
========

Deployment
----------

```bash
git clone _thisrepo_
cd gertrude
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements.txt
./manage.py update_git https://url/to/your/pages/repo
```

Then to run the *development* server :

```bash
./manage.py runserver
```
