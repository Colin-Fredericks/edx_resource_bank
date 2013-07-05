#!/usr/bin/python

import sys
import csv
import re
import itertools
import MySQLdb

""" Example of SQL stuff
		
		cur.execute("SELECT * FROM YOUR_TABLE_NAME")

		# print all the first cell of all the rows
		for row in cur.fetchall() :
		print row[0]

"""




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
			
			# Take the second column and make a Collection out of it, if one doesn't already exist. 
			# Add this resource to the collection from column 2.
			# if 
			# 	collection = row[1]
			# cur.execute("INSERT INTO RDB_resource (collection) VALUES (%s)", row[1])
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
			print (sql_query)
			
			# next line in file -- handled automatically by the "for reader in row" statement.
			# Next entry in database -- handled automatically by the fact that we're INSERTing whole rows at a time.

		# End loopy-loo

	# Close the file -- done automatically via the "with" command
	# Clean up the database stuff
	
	print cur.execute("SELECT * FROM RDB_resource")

	db.commit()
	cur.close()
	db.close()

# Done with main


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])