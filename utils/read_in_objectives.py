#!/usr/bin/python

import sys
import csv					# routines for for Comma Separated Value files
import re					# regular expressions, so I can escape text that would go into SQL
import mysql.connector		# python-to-mySQL translator


##################
# Important notes:
# The code to associate learning objectives with resources is in read_in_file.py
##################

# Function that converts things
def main(argv):

	# Check for correct usage
	if not argv:
		sys.exit("Please specify an input file in csv format.")
	if len(argv) == 1:
		sys.exit("Usage: python read_in_objectives.py whatever.csv")
	if argv[1] == "-h":
		sys.exit("Usage: python read_in_objectives.py whatever.csv")

	# Counter so we can give some useful output
	added_objectives = 0

	# Take in a filename from the command line
	filename = str(sys.argv[1])

	# open the file
	with open(filename, 'rb') as csvfile:

		# Connect to the database
		db = mysql.connector.connect(user="resource_mangler",
			passwd="1l0v3dat3r",
			host="localhost",
			database="edxresources",
			buffered=True)

		# Create a Cursor object with which to execute queries
		cur = db.cursor() 
		
		# Create a CSV reader
		spreadsheet = csv.reader(csvfile)

		# Skip the first row. It's full of headers.
		next(spreadsheet, None)

		# Loopy-loo: until we're done with the file...
		for row in spreadsheet:

			# Some rows may be blank in this file. If there's nothing in column 2, skip the row.	
			if row[1]:

				# Set all the variables that we're going to insert via SQL.
				# Row 1 is the long name / description
				learning_objective = row[0]
				# Row 2 is the short name
				short_name = row[1]
			
				# ignore any other columns.
				
				# If the learning objective already exists, skip to the next line.
				cur.execute("SELECT id FROM RDB_learning_objective WHERE BINARY learning_objective = BINARY %s", (learning_objective,))

				try:
					# Set the collection id to that.
					LO_id = cur.fetchone()
				except TypeError:
					# Unless it's null or something, in which case panic and run in circles.
					sys.exit("Error getting Learning Objective ID.")

				if not LO_id:

					# Run an"INSERT" command add the learning objective
					cur.execute("INSERT RDB_learning_objective (short_name, learning_objective) VALUES (%s, %s) ", (short_name.decode('latin'), learning_objective.decode('latin')))
					added_objectives += 1
			
			# next line in file -- handled automatically by the "for row in spreadsheet" statement.
			# Next entry in database -- handled automatically by the fact that we're INSERTing whole rows at a time.

		# End loopy-loo

	# Close the file -- done automatically via the "with" command
	# Clean up the database stuff: Commit all changes, close cursor and database.
	db.commit()
	cur.close()
	db.close()

	print " Added " + str(added_objectives) + " learning objectives."

# Done with main


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])