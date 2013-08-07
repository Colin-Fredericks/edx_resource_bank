Reading in a Course
====================

This folder contains a toy course - about half of Mechanics ReView - and a script entitled read\_in\_course.py that reads it into the database created in other parts of this project.

Here's the gist of how it works.

edX courses are organized by an XML structure that goes about like this:

    Course Alpha
    +---Chapter I
    |   +---Section 1
    |   |   +---Vertical a
    |   |   |   +---Resource i
    |   |   |   +---Resource ii
    |   |   +---Vertical b
    |   |       +---Resource i
    |   |       +---Resource ii
    |   +---Section 2
    |   |   +---Vertical a
    etc.
        

These different elements can be either separate files, or defined inline. If you wanted, you could have the whole course as a single XML document (and then you should shoot yourself). In our course, some of them are files and some are inline.

**The course-reading script does this:**

* Recursively traverses the structure in the XML file
* Picks up display\_names and tag types along the way
* Assigns the resources to the database based on the information
 * A "resource" is a file without any links to files farther down on the heirarchy. This is usually an HTML file or a problem file.
* Dumps in the entire text of the resource while it's at it
* Creates collections that tell us what contains that resource (e.g. what course, chapter, section, and vertical it's part of)

**It does not:**

* Auto-generate descriptions
* Include graphics or other linked files (though this feature could be added)
* Notice `<description>` or `<video>` files yet. (though this could also be added)
* Auto-detect older versions already in the database (though it does skip perfect duplicates)
* Create collections based on anything else
* Work perfectly as of 

**Handling Exceptions**

The XML structure for edX is sometimes not strict enough. You can use a filename attribute, or a url\_name attribute. You can define display\_names in multiple different places. You can store an HTML file with a .xml extension. 50% or more of this script is for handling exceptions.

* The traversal is not recursive if a container (e.g. sequence, vertical) is defined inline.
* The script uses filenames if it can't get a display\_name.
 * This can sometimes cause issues for inline definitions.
* 