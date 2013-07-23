#########
# The goal here is to strip all the text out of an existing edX course and 
#  use it to provide the "text" fields for the resource databse.
# We're traversing the edXML file structure looking for filepaths that end in resources, 
#  going as deep as we need to, and creating resources along the way.
# The general approach is recursive.
#########

# Take a filepath as an argument
# Open that file
	# For every line in the file...
		# Use regular expressions to get the list of filepaths from filename="" or url_name=""
		# If that list of filepaths is not empty:
			# For every file in the list of filepaths:
				# Get the filepath and display_name.
				# Run this function with that filepath and display_name as arguments.
		# If that list of filepaths is empty:
			# We're going to INSERT a new resource into the database.
			# Take the display_name, escape it, and dump it into the "name" field.
			# Take the entire text of this file, escape it, and dump it into the "text" field.
			# Set hide_info and is_deprecated both = False by default
			# If the file ends with .html:
				# resource_type="html"
			# If the file ends with .problem.xml or just .xml:
				# resource_type="problem"
				# Use regex to set problem_type based on whether it's <multiplechoice>, <numericresponse>, <formularesponse>, etc.
				# If no problem_type found, go back and set the resource_type to "other"
			# Other required items that we will also need:
				# Learning Objectives!!
				# Description
	# Move to the next line - should be done automatically by the for loop
# Close the file - should be done automatically using the "with open" approach.
##########

# What if the resource already exists in the database? 
# How to find the appropriate resource? Display_name seems to be all we have.
# May need to have existing resources include a "link to source" field and use those instead.
# Probably need to do a this-to-that table by hand.