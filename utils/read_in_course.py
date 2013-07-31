#!/usr/bin/python

#########
# The goal here is to strip all the text out of an existing edX course and 
#  use it to provide the "text" fields for the resource databse.
# We're traversing the edXML file structure looking for filepaths that end in resources, 
#  going as deep as we need to, and creating resources along the way.
# The general approach is recursive.
#########

# Take a filepath, tag type, and display_name as arguments
# Open that file
	# For every line in this file:
		# If this line has a <chapter> or <sequential> or <vertical> tag...
			# Escape the display_name and dump it in current_collection.
		# If this line has a filename="" or url_name="" attribute:
			# Get the filepath, tag type, and the display_name from the same line.
			# Run this function with those three things as arguments.
			# Add to the number of filepaths found in this way.
		# Move to next line (done automatically by the for loop)
	# If there are no filepaths found in this whole file:
		# We're going to INSERT a new resource into the database.
		# Take the current display_name, escape it, and dump it into the "name" field.
		# Take the entire text of this file, escape it, and dump it into the "text" field.
		# Set hide_info and is_deprecated both = False by default
		# Use the tag type to set the resource type to html or problem.
			# (What to do with videos?)
		# If the resource type is problem:
			# Use regex to set problem_type based on whether it's <multiplechoice>, <numericresponse>, <formularesponse>, etc.
			# If no problem_type found, go back and set the resource_type to "other"
		# Other required items that we will also need:
			# Learning Objectives!!
			# Description
		# Run the MySQL INSERT command.
		# Link this resource to the current_collection, creating the collection if necessary.
			# (The Collection_Creator function does this just how I want.)
# Close the file - should be done automatically using the "with open" approach.
##########

# What if the resource already exists in the database? 
# How to find the appropriate resource? Display_name seems to be all we have.
# May need to have existing resources include a "link to source" field and use those instead.
# Probably need to do a this-to-that table by hand.


####################################################
# Automated Collection Creation!
####################################################

def Collection_Creator(collection, cur, resource_id):

	added_collections = 0

	# Check to see if a collection with this name already exists. 
	cur.execute("SELECT id FROM RDB_collection WHERE name = %s", collection)

	try:
		# Set the collection id to that.
		collection_id = cur.fetchone()[0]
	except TypeError:
		# Unless it's null or something, in which case set it to zero.
		collection_id = 0

	# If not, create the collection.
	if not collection_id:

		# A big INSERT command to create the collection.
		collection_query = "INSERT INTO RDB_collection "

		collection_query += "(name, "
		collection_query += "collection_type, "
		collection_query += "is_sequential, "
		collection_query += "is_deprecated, "
		collection_query += "creation_date) "

		collection_query += "VALUES ('"

		collection_query += re.escape(collection) + "', '" 
		collection_query += "other" + "', '" 
		collection_query += "0"  + "', '" # is_sequential
		collection_query += "0"  + "', '" # is_deprecated
		collection_query += "2001-01-01" + "')" # creation_date

		cur.execute(collection_query)
		added_collections += 1
	
		# Get the ID of the collection I just created.
		collection_id = cur.lastrowid
	
	# Add this resource to the collection.
	resource_insert_query = "INSERT INTO RDB_collection_included_resources "
	resource_insert_query += "(collection_id, "
	resource_insert_query += "resource_id) "
	resource_insert_query += "VALUES ('"
	resource_insert_query += str(collection_id) + "', '"
	resource_insert_query += str(resource_id) + "')"

	cur.execute(resource_insert_query)

	return added_collections

