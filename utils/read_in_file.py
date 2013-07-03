# Function that converts things
# Take in a filename from the command line

# open the file
spreadsheet = open('name_of_file', 'r')

# Loopy-loo: until we're done with the file
	
	# read a line of the file

	# break it up by CSV pieces

	# Ignore first column (index)

	# Take the second column and make a Collection out of it, if one doesn't already exist. 
	# Add this resource to the collection from column 2.

	# Put the third column into the "name" field

	# If the fourth column has the word "problem", mark resource_type = problem

	# Skip column five
	# Check to see if Columns 6, 7, 8 already exist as learning objectives.
		# if not, create them.
	# Add this resource to the learning objectives for columns 6, 7, 8

	# Put column 9 into the "description" field

	# Put column 10 in as a custom text field named "LC SYMB"

	# End loopy-loo

# Close the file
