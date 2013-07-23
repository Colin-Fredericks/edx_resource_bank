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
			# This should eventually be done by reading the headers.

			name = row[0]
			# If the second column has the word "problem", mark resource_type = problem. Otherwise, call it "other" for now.
			# More sophisticated parsing later.

			if row[1].find("problem") == -1:
				resource_type = 'other'
			else:
				resource_type = 'problem'

			description = row[2]

			learning_objectives = [row[3], row[4], row[5]]

			if row[6]:
				# Should check for right values
				is_deprecated = row[6]
			else:
				is_deprecated = '0'
			
			if row[7]:
				# Should check for right values
				hide_info = row[7]
			else:
				hide_info = '0'

			# Eventually we want to read this from a separate file rather than from a CVS cell
			text = row[8]

			resource_file = row[9]

			if row[10]:
				# Should run a check here to make sure it's on the accepted list.
				grade_level = row[10]
			else:
				grade_level = 'any'

			intended_use = row[11]

			license = row[12]

			license_link = row[13]

			license_other_notes = row[14]

			source = row[15]

			if row[16]:
				language = row[16]
			else:
				language = 'English'
			
			author = row[17]

			comments = row[18]

			if row[19]:
				# Should run a check here to make sure it's a date in the right format
				creation_date = row[19]
			else:
				creation_date = '2001-01-01'

			if resource_type == 'problem':
				if row[20]:
					# Should run a check here to make sure it's on the accepted list.
					# Then again, we're blocking out future problem types with that...
					problem_type = row[20]
				else:
					problem_type = 'other'
			else:
				problem_type = 'not_a_problem'

			solutions_hints_etc = row[21]

			collection = row[22]

			# custom text rows need some work.			

			# Check to see if there's a duplicate entry in the database already
			# If so, check for new Learning Objectives and match them up if necesasry. 
			# Then skip this row and go back to the top of the "for" loop.
			# If there's no duplicate, insert this resource.

			sql_start = "SELECT * FROM RDB_resource  WHERE"
			
			sql_left = "(name, "
			sql_left += "resource_type, "
			sql_left += "description, "
			sql_left += "is_deprecated, "
			sql_left += "hide_info, "
			sql_left += "text, "
			sql_left += "resource_file, "
			sql_left += "grade_level, "
			sql_left += "intended_use, "
			sql_left += "license, "
			sql_left += "license_link, "
			sql_left += "license_other_notes, "
			sql_left += "source, "
			sql_left += "language, "
			sql_left += "author, "
			sql_left += "comments, "
			sql_left += "creation_date, "
			sql_left += "problem_type, "
			sql_left += "solutions_hints_etc) "
			
			sql_middle = "= ('"
			
			sql_right = re.escape(name) + "', '" 
			sql_right += resource_type  + "', '" 
			sql_right += re.escape(description)  + "', '" 
			sql_right += is_deprecated  + "', '" 
			sql_right += hide_info  + "', '" 
			sql_right += re.escape(text)  + "', '"
			sql_right += resource_file  + "', '"
			sql_right += grade_level  + "', '"
			sql_right += intended_use  + "', '"
			sql_right += re.escape(license)  + "', '"
			sql_right += re.escape(license_link)  + "', '"
			sql_right += re.escape(license_other_notes)  + "', '"
			sql_right += source  + "', '"
			sql_right += language  + "', '"
			sql_right += re.escape(author)  + "', '"
			sql_right += re.escape(comments)  + "', '"
			sql_right += creation_date  + "', '"
			sql_right += problem_type  + "', '"
			sql_right += re.escape(solutions_hints_etc)  + "')"

			sql_query = sql_start + sql_left + sql_middle + sql_right

			if cur.execute(sql_query):
				print "Skipping duplicate entry " + name

				"""
				This section is not currently working properly, but it's fairly close.
				I'd like to insert *only new or different* learning objective links.
				
				# Check to see if this duplicate has the same learning objectives as the new item.
				# If so, add them. If not, continue skipping.
				resource_id = cur.fetchone()[0]
				cur.execute("SELECT learning_objective_id FROM RDB_resource_learning_objective WHERE resource_id = %s", resource_id)
				old_objective_ids = cur.fetchall()
				print 'old_objective_ids = ' + str(old_objective_ids)
				if old_objective_ids is not None:
					old_LO_list = []
					for idnum in old_objective_ids:
						cur.execute("SELECT short_name FROM RDB_learning_objective WHERE id = %s", idnum)
						old_LO_list += cur.fetchone()
				# Pad out the old list, because the new list may have blanks.
				old_LO_list += ( [''] * (len(learning_objectives) - len(old_LO_list)))
				print str(len(old_LO_list)) + str(old_LO_list)
				print str(len(learning_objectives)) + str(learning_objectives)
				if learning_objectives == old_LO_list:
					print "Skipping duplicate entry " + name
				else:
					print "Found near-duplicate entry with new LOs. Linking."
					linked_objectives += Associate_Learning_Objectives(learning_objectives, cur, resource_id)
				"""

			else:

				# Since it's not a duplicate entry...
				# Run an "INSERT" command to put in this resource
				sql_start = "INSERT RDB_resource "
				sql_middle = "VALUES ('" 

				sql_query = sql_start + sql_left + sql_middle + sql_right
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
			
			# next line in file -- handled automatically by the "for row in spreadsheet" statement.
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