#!/usr/bin/python

import sys
import csv
import re # Regular Expressions, so I can escape things that would go into SQL
import MySQLdb


# Function that converts things
def main(argv):

	# Check for correct usage
	if not argv:
		sys.exit("Please specify an input file in csv format.")
	if len(argv) == 1:
		sys.exit("Usage: python read_in_file.py whatever.csv")
	if argv[1] == "-h":
		sys.exit("Usage: python read_in_file.py whatever.csv")

	# Take in a filename from the command line
	filename = str(sys.argv[1])

	# open the file
	with open(filename, 'rb') as csvfile:

		# Connect to the database
		db = MySQLdb.connect(host="localhost",
			user="resource_mangler",
			passwd="1l0v3dat3r",
			db="edxresources")

		# Create a Cursor object with which to execute queries
		cur = db.cursor() 
		
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
			# Put column 9 into the "description" field.
			description = row[8]
			# Set some required fields automatically.
			hide_info = '0'
			is_deprecated = '0'
			
			#
			# Skip column five
			# Check to see if Columns 6, 7, 8 already exist as learning objectives.
				# if not, create them.
			# Add this resource to the learning objectives for columns 6, 7, 8
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

			# Get the ID of the resource I just created
			resource_id = cur.lastrowid


			# Check to see if a collection with this name already exists. 
			collection_id = cur.execute("SELECT id FROM RDB_collection WHERE name = %s", collection)
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

			
			# next line in file -- handled automatically by the "for reader in row" statement.
			# Next entry in database -- handled automatically by the fact that we're INSERTing whole rows at a time.

		# End loopy-loo

	# Close the file -- done automatically via the "with" command
	# Clean up the database stuff: Commit all changes, close cursor and database.
	db.commit()
	cur.close()
	db.close()

# Done with main


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])