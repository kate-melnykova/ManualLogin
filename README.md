## Manual login and logout using cookies
This package is part of learning basics
of cookies.

# Installation
To start the code, please install `docker` and `docker-compose`.
Run the following lines in the terminal:

`$ docker-compose up -d --build`

and

`$ docker-compose up`

# Getting started
This package implements:
* blueprint login and logout interface and functions
 (currently, just a package). Registration interface
 will be added soon.
* `login_required` decorator for route handlers
 that checks that the AES encoded username
 stored in cookies correpond to a user in user
 database
 
The package works as follows. If the user is logged in, he or she cannot
access the login page and is redirected to
the route page. If the user is not logged it,
he or she is not able to access the logout page
and is redirected to the login page.

The username is stored in cookies (sessional or
permanent) and is protected via the AES encrypting.

The username database is implemented using Redis.  