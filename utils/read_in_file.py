#!/usr/bin/python

import sys
import csv
import MySQLdb

""" Example of SQL stuff
		# Use all the SQL you like
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

		"""		# Connect to the database
				db = MySQLdb.connect(host="localhost",
								user="resource_mangler",
								passwd="1l0v3dat3r",
								db="edxresources")

				# Create a Cursor object with which to execute queries
				cur = db.cursor() 
		"""
		# Create a CSV reader
		spreadsheet = csv.reader(csvfile)

		# Loopy-loo: until we're done with the file...
		for row in spreadsheet:
	
			# Take the second column and make a Collection out of it, if one doesn't already exist. 
			# Add this resource to the collection from column 2.
			# currently testing by printing it out
			print row[2]

			# Put the third column into the "name" field

			# If the fourth column has the word "problem", mark resource_type = problem

			# Skip column five
			# Check to see if Columns 6, 7, 8 already exist as learning objectives.
				# if not, create them.
			# Add this resource to the learning objectives for columns 6, 7, 8

			# Put column 9 into the "description" field

			# Put column 10 in as a custom text field named "LC SYMB"
			
			# next line -- handled automatically by the "for reader in row" statement

		# End loopy-loo

	# Close the file -- done automatically via the "with" command

# Done with main


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])