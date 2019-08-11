## Loxodonta Localizer V1.0


#### Installation Instructions

**Setup environment**
```bash
#first, install Python 2.7,  pip and git
git clone https://github.com/kaizhao86/loxodontalocalizer
cd loxodontalocalizer
pip install --user -r requirements.txt
```

**Build database, if needed**
```bash
python manage.py makemigrations #make sure there's no missing migrations
python manage.py migrate 
```
**Make a user account for /login, for editing data**

You'll need to edit the database directly using a tool like *DB Browser for SQLite* for certain operations
```bash
python manage.py createsuperuser #make an admin user name if you need one
```
**Finally, start the server**
```bash
python manage.py runserver
```

*Note* We use Zappa to host Loxodonta Localizer on Amazon Lambda