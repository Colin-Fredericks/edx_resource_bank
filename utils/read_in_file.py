#!/usr/bin/python

import sys
import csv			# routines for for Comma Separated Value files
import re			# regular expressions, so I can escape text that would go into SQL
import MySQLdb		# python-to-mySQL translator

##################
# Important notes:
# Reading in learning objectives is done in read_in_objectives.py
##################

# Function that converts things
def main(argv):

	# Check for correct usage
	if not argv:
		sys.exit("Please specify an input file in csv format.")
	if len(argv) == 1:
		sys.exit("Usage: python read_in_file.py whatever.csv")
	if argv[1] == "-h":
		sys.exit("Usage: python read_in_file.py whatever.csv")

	# trackers so that we can give some output
	added_resources = 0
	added_collections = 0
	linked_objectives = 0 

	# Take in a filename from the command line
	filename = str(sys.argv[1])

	# open the file
	with open(filename, 'rbU') as csvfile:

		# Connect to the database
		db = MySQLdb.connect(host="localhost",
			user="resource_mangler",
			passwd="1l0v3dat3r",
			db="edxresources")

		# Create a Cursor object with which to execute queries
		cur = db.cursor() 
		
		# Check to see whether learning objectives are already present.
		# If not, exit, telling the user to read some in first.
		# unfinished

		# Create a CSV reader
		spreadsheet = csv.reader(csvfile)

		# Skip the first row. It's full of headers.
		next(spreadsheet, None)

		# Loopy-loo: until we're done with the file...
		for row in spreadsheet:
	

			# Set all the variables that we're going to insert via SQL.
			# The second column is the name of the collection. Unit 1, Homework 6, etc.
			collection = row[1]
			# Put the third column into the "name" field.
			name = row[2]
			# If the fourth column has the word "problem", mark resource_type = problem. Otherwise, call it "other" for now.
			# More sophisticated parsing later.
			if row[3].find("problem") == -1:
				resource_type = 'other'
			else:
				resource_type = 'problem'
			# Get the learning objectives from columns 6,7,8 in the file
			learning_objectives = [row[5], row[6], row[7]]
			# Put column 9 into the "description" field.
			description = row[8]
			# Set some required fields automatically.
			hide_info = '0'
			is_deprecated = '0'
			
			#
			# Skip column five
			#
			# Put column 10 in as a custom text field named "LC SYMB"
			#


			# Run one big "INSERT" command to put it all in.
			sql_query = "INSERT RDB_resource "
			
			sql_query += "(name, "
			sql_query += "resource_type, "
			sql_query += "description, "
			sql_query += "is_deprecated, "
			sql_query += "hide_info, "
			sql_query += "text, "
			sql_query += "resource_file, "
			sql_query += "grade_level, "
			sql_query += "intended_use, "
			sql_query += "license, "
			sql_query += "license_link, "
			sql_query += "license_other_notes, "
			sql_query += "source, "
			sql_query += "language, "
			sql_query += "author, "
			sql_query += "comments, "
			sql_query += "creation_date, "
			sql_query += "problem_type, "
			sql_query += "solutions_hints_etc) "
			
			sql_query += "VALUES ('"
			
			sql_query += re.escape(name) + "', '" 
			sql_query += resource_type  + "', '" 
			sql_query += re.escape(description)  + "', '" 
			sql_query += is_deprecated  + "', '" 
			sql_query += hide_info  + "', '" 
			sql_query += ""  + "', '" # text, will need to escape here too
			sql_query += ""  + "', '" # resource_file
			sql_query += "any"  + "', '" # grade_level
			sql_query += ""  + "', '" # intended_use
			sql_query += ""  + "', '" # license
			sql_query += ""  + "', '" # license_link
			sql_query += ""  + "', '" # license_other_notes
			sql_query += ""  + "', '" # source
			sql_query += "English"  + "', '" # language
			sql_query += ""  + "', '" # author
			sql_query += ""  + "', '" # comments
			sql_query += "2001-01-01"  + "', '" # creation_date
			sql_query += "not_a_problem"  + "', '" # problem_type
			sql_query += ""  + "')" # solutions_hints_etc

			cur.execute(sql_query)
			added_resources += 1

			# Get the ID of the resource I just created
			resource_id = cur.lastrowid

			################
			# Automated Collection Creation!
			# The Collection_Creator function returns the number of new collections that were added. Add 'em up.
			###############

			added_collections += Collection_Creator(collection, cur, resource_id)

			################
			# Associate the resource with Learning Objectives!
			# The Associate_Learning_Objectives function returns the number of objectives that were linked. Add 'em up.
			###############
			
			linked_objectives += Associate_Learning_Objectives(learning_objectives, cur, resource_id)
			
			# next line in file -- handled automatically by the "for reader in row" statement.
			# Next entry in database -- handled automatically by the fact that we're INSERTing whole rows at a time.

		# End loopy-loo

	# Close the file -- done automatically via the "with" command
	# Clean up the database stuff: Commit all changes, close cursor and database.
	db.commit()
	cur.close()
	db.close()
	
	print " Added " + str(added_resources) + " resources,"
	print " with " + str(linked_objectives) + " links to learning objectives."
	print " Added " + str(added_collections) + " new collections."

# Done with main


####################################################
# Associate the resource with Learning Objectives
####################################################

def Associate_Learning_Objectives(learning_objectives, cur, resource_id):


	linked_objectives = 0

	# Go through all 3 of them. 
	for LO in learning_objectives:
		if LO:
			# Find the learning objective object with the correct short name
			cur.execute("SELECT id FROM RDB_learning_objective WHERE short_name = %s", LO)

			try:
				# Set the LO id to that.
				LO_id = cur.fetchone()[0]
			except TypeError:
				# Unless it's null or something, in which case set it to zero.
				LO_id = 0

			# If they already exist as objectives, associate this resource with them.
			if LO_id:
				# Connect that LO with the current resource, resource_id
				LO_insert_query = "INSERT INTO RDB_resource_learning_objective "
				LO_insert_query += "(learning_objective_id, "
				LO_insert_query += "resource_id) "
				LO_insert_query += "VALUES ('"
				LO_insert_query += str(LO_id) + "', '"
				LO_insert_query += str(resource_id) + "')"

				cur.execute(LO_insert_query)
				linked_objectives += 1 

			else:
				# If the LO doesn't exist yet, complain about it.
				print LO + " does not yet exist as a learning objective."
			
		else:
			# If no LO specified, just skip it.
			pass

	return linked_objectives


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


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])