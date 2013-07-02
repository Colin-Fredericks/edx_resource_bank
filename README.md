Resource Database
====================

This repository is a collection of Python code. It uses [Django](https://docs.djangoproject.com/en/1.5/) to set up a mySQL database for resources in an online course (in our case, edX).

So far it's not connected to anything else. Don't look at this imagining that you'll figure out how edX works. We're still in the infant stages of development, and I'm learning django, python, and SQL as I go along.

Folders
--------

resource_bank is the project.
RDB is the app. Stands for Resource DataBase.
uploads is where uploaded files go by default. Nothing there at the moment.

Dependencies
--------------

You'll have to create the mySQL database yourself. Check out resource_bank/settings.py to see/change names and passwords for that database.

We may end up using [Fieldmaker](https://django-fieldmaker.readthedocs.org/en/latest/index.html), or we may not. It's still included in various files, so you'll need that if you want to run this.

I'd like to get [South](http://south.aeracode.org/) working, but damned if I can figure it out right now.

Status
--------

Still fiddling around.

Getting the interface working properly is a big priority. Right now some things are going to be completely unusable once we have 1000 different problems in here.

Importing data via script, without having to type it all into the admin interface.

Oddities and details
--------------------

I'm doing this on MacOS 10.8.whateveritistoday. Hopefully nothing in here depends on that, but I wanted to mention it just in case.