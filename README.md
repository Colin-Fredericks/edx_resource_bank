Resource Bank
====================

DEFUNCT
-------

This code should no longer be used to parse edX's XML documents. It's been over three years, and things have changed there. It is maintained here (for loose definitions of "maintain") solely as a historical curiosity.

---

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

This code is written for Python 2.7.2. It should work in 2.7.5, but will [need some work](http://docs.python.org/2/library/2to3.html) before you use it with Python 3.

You'll have to create the mySQL database yourself. Check out resource_bank/settings.py to see/change names and passwords for that database. The django code will take care of creating any tables within the database.

You'll need the [Connector/Python](https://dev.mysql.com/downloads/connector/python/) package. We used to use the MySQLdb package, but it doesn't install with python 3 on Windows, and hasn't been updated in years, so we're going with this one. You'll also need the python "CSV" and "re" packages, but they seem to be built into most distributions. The course-reader needs "lxml" and "collections" as well.

[Fieldmaker](https://django-fieldmaker.readthedocs.org/en/latest/index.html) has been removed for now, and is unlikely to return. It would be nice to get [South](http://south.aeracode.org/) working so as to not have to delete the database.

Status
------

The import scripts are working fairly well, including the one to import an entire course from the edXML. Much functionality still to be added.

To Do list:
-----------

* Enable the course read-in script to handle video tags. Later on it will also probably be necessary to get it to handle things like "conditional" tags, but that's a whole other story.

* Right now nothing reads in analytics results. Those will be necessary for this project to really reach its potential.

* There's an "is_sequential" entry for collections, but nothing to actually keep the items in sequence yet (and no way to change that sequence).

* Right now you still need to read in Learning Objectives before reading in a file if you want to link them properly to each other.

* Showing the "extensive" view is very time-consuming and processor-intensive. This may be because of how the collections are organized and how the display is generated. (Right now it goes: for every resource, loop through all the collections, and for each collection, loop through all the resources in that collection to see if it's the one you're interested in. And I'm pretty sure each comparison is two database calls.)

* The course read-in script should be tested with course XML exported from Studio.

* There should be a read-out script as well, that takes a container and creates a course or a portion of one from the resources in the database.

* It should be fairly easy to read a file's modification date and use that as the "creation_date".

* Custom text should be reintegrated into the database. Tried to do it with Fieldmaker, but there should be a better way.

Oddities and details
--------------------

Originally created in MacOS 10.8.4. It uses Python 2.7.2.
