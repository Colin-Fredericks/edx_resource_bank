Resource Bank
====================

This repository is a collection of Python code. It uses [Django](https://docs.djangoproject.com/en/1.5/) to set up a mySQL database for resources in an online course (in our case, edX).

So far it's not connected to anything else. Don't look at this imagining that you'll figure out how edX works. We're still in the infant stages of development, and I'm learning django, python, and SQL as I go along.

Folders
--------

* *resource_bank* is the project.

* *RDB* is the app. Stands for Resource DataBase. There's another ReadMe file in there, you should check it out.

* *uploads* is where uploaded files go by default. Nothing there at the moment.

* *utils* is where the import-from-csv scripts are, as well as sample files.
 * Within *utils* is *toy_course*, which has a bare-bones framework of Mechanics ReView and a script to read it in. There's yet another ReadMe file there that explains how it works.

Dependencies
--------------

You'll have to create the mySQL database yourself. Check out resource_bank/settings.py to see/change names and passwords for that database. The django code will take care of creating any tables within the database.

You'll need the [python mySQL](http://sourceforge.net/projects/mysql-python/) package. You'll also need the python "CSV" and "re" packages, but they seem to be built into most distributions.

[Fieldmaker](https://django-fieldmaker.readthedocs.org/en/latest/index.html) has been removed for now, but may make its way back in at some point. I'd also like to get [South](http://south.aeracode.org/) working, but damned if I can figure it out right now.

Status
--------

The script to import an entire edX course from the XML files is just getting started.

The import scripts are working fairly well. They even check for (and rejects) duplicate entries now! There are separate scripts to read in resources and learning objectives.

Getting the interface working properly (i.e. usable with 1000 entries) is not as big a priority as it used to be. Starting to rethink this as more of a back-end system.

Oddities and details
--------------------

I'm doing this on MacOS 10.8.whateveritistoday. Hopefully nothing in here depends on that, but I wanted to mention it just in case.
