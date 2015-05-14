## dashto.net
Python 3 web application

### Installation
For deployment:
```
python setup.py install
```

For development:
```
python setup.py develop
```

### Database setup

Alter the database to match the latest schema:
```
alembic -c [development/production].ini upgrade head
```

Generate a migration to match the schema defined in models.py:
```
alembic -c [development/production].ini revision --autogenerate -m "message goes here"
```

Roll back the latest upgrade:
```
alembic -c [development/production].ini downgrade -1
```

### Creating a user

Create the first user so you can log in to the app:
```
python create_user.py -c [development/production].ini
```

### Running the web server
```
pserve [--reload] [development/production].ini
```

### Running the chat server
```
python chat_server.py -c [development/production].ini
```
