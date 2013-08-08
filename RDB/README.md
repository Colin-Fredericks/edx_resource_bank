Resource Database
====================

You can read what's in the database in the models.py file. In case you don't read django yet, this ReadMe is a summary of that and how it's set up.

The main items in the database are:
* **Resources**
* Items that hold descriptors for resources, such as:
 * Learning Objectives
 * Tags
 * Keywords
 * Code Dependencies
 * Analytics
* **Collections**
* Items that hold descriptors for Collections

Resources
-----------

Resources each have...

* name (required)
* resource\_type (required)
* description (required)
* is\_deprecated (required)
* hide\_info (required)
* text
* resource\_file
* grade\_level
* intended\_use
* license
* license\_link
* license\_other\_notes
* source
* language
* author
* comments
* creation\_date
* problem\_type
* solutions\_hints\_etc

They also have multiple different items linked to them (as many-to-many fields or one-to-many fields) that record other info.

Resource-Linked Items
-----------

* Learning Objectives (we'd like these to be required)
* Tags
* Keywords
* Code Dependencies
* Analytics

Each of these is a separate database sheet.


Collections
-----------

Collections each have...

* name
* collection\_type
* is\_sequential
* is\_deprecated
* creation\_date

They also have multiple different items linked to them (as many-to-many fields or one-to-many fields) that record other info. That's how they say which items are included in the collection.

The collection types are page, module, chapter, related items, versions, and "other". There is no "course" collection type, since that seemed to be an object that needed more specific metadata.


Collection-Linked Items
-----------

* included\_resources
* code\_dependencies
* learning\_objectives\_broad
 * You can find the learning objectives of individual resources within a collection by running a query, but the collection might also have an overarching learning objective that's broader than the one you might see for an individual resource. Thus this separate category.