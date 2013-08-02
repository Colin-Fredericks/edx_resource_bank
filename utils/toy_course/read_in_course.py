#!/usr/bin/python

#########
# The goal here is to strip all the text out of an existing edX course and 
#  use it to provide the "text" fields for the resource databse.
# We're traversing the edXML file structure looking for filepaths that end in resources, 
#  going as deep as we need to, and creating resources along the way.
# The general approach is recursive.
#########



import sys
import re			# regular expressions for searching and escaping
import MySQLdb		# python-to-mySQL translator
# May need to import some sort of XML parser? 
# What I'm doing is fairly simple, so perhaps not.

# Main takes in arguments, connects to the database, and runs BigLoop.
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

	"""   Leaving out database for now.
	# Connect to the database
	db = MySQLdb.connect(host="localhost",
		user="resource_mangler",
		passwd="1l0v3dat3r",
		db="edxresources")

	# Create a Cursor object with which to execute queries
	cur = db.cursor() 
	
	# Delete the line below when we're ready to use the database.
	"""
	cur = ""
	
	collection_collection = [filename, ]
		
	BigLoop(filename, "", "", collection_collection, 0, cur)


# This is the recursive function that does most of our work.
def BigLoop(filepath, tag_type, display_name, cc, depth, cur):

	collection_collection = cc[:]

	if depth > 10:
		sys.exit("Potential infinite loop detected. Exiting. Check for files that reference themselves?")

	# trackers so that we can give some output
	# I just realized these will all need to get passed if we're going to actually use them.
	# added_resources = 0
	# added_collections = 0
	# linked_objectives = 0 
	filepaths_found = 0

	# open the file
	try:
		with open(filepath, 'rbU') as xmlfile:


			# For every line in this file:
			for line in xmlfile:
			
				"""    Still working on this section. Commented out for clean upload.
				# I'm concerned that we're only keeping one collection.
				# Resources should belong to multiple collections, and I think this only adds it to the last one found.
				# If this line has a <chapter> or <sequential> or <vertical> tag...
				if '<chapter' in line or '<sequential' in line or '<vertical' in line:

					# Escape the display_name and dump it in current_collection.
					dn = re.search('display_name="(.*?)"', line)
					if dn:
						if re.escape(dn.group(1)) not in collection_collection:
							collection_collection = collection_collection + [re.escape(dn.group(1))]
					else:
						if re.escape(xmlfile.name) not in collection_collection:
							collection_collection = collection_collection + [re.escape(xmlfile.name)]
					
					print collection_collection
				"""


				# If the tag on this line closes on the same line, attempt to open the file it links to and traverse the file tree.
				# If it's not self-closing, it doesn't actually link to a file. Move on.

				if re.search('/>',line):

					# If this line has a filename="" attribute, use that and go there:
					if re.search('filename="(.*?)"', line):
			
						# Get the filepath, tag type, and the display_name from the same line.
						filepath = re.search('filename="(.*?)"', line).group(1)
						tag_type = re.search('<(\S+?) ',line).group(1)
						dn = re.search('display_name="(.*?)"', line)
						if dn:
							display_name = dn.group(1)
						else:
							display_name = ''

						# Correct the filename - add folder and .xml if needed.
						if '<problem ' in line:
							if filepath.find("problems/") != 0:
								filepath = 'problems/' + filepath   # Note the s.
							filepath = filepath + '.xml'
						else:
							filepath = FixPath(filepath, line)
					
						# Run this function with those three things as arguments.
						# print "opening filename " + filepath
						BigLoop(filepath, tag_type, display_name, collection_collection, depth+1, cur)
						filepaths_found += 1
				

					# If this line has a url_name="" attribute, things work slightly differently:
					elif re.search('url_name="(.+?)"',line):

						# Get the filepath, tag type, and the display_name from the same line.
						filepath = re.search('url_name="(.*?)"', line).group(1)
						tag_type = re.search('<(\S+?) ',line).group(1)
						dn = re.search('display_name="(.*?)"', line)
						if dn:
							display_name = dn.group(1)
						else:
							display_name = ''
					
						# Correct the filepath. Swap out colons, add folder and .xml if needed.
						filepath = filepath.replace(':','/')
						if '<problem ' in line:
							if filepath.find("problem/") != 0:
								filepath = 'problem/' + filepath   # Note the lack of s.
							filepath = filepath + '.xml'
						else:
							filepath = FixPath(filepath, line)
				
						# Run this function with those three things as arguments.
						# print "opening urlname " + filepath
						BigLoop(filepath, tag_type, display_name, collection_collection, depth+1, cur)
						filepaths_found += 1

				# Move to next line (done automatically by the for loop)

			# If there are no self-closing tags with filepaths found in this whole file:
			if filepaths_found == 0:

				# We're going to INSERT a new resource into the database.
							
				# It is possible for the display_name to be blank. If not:
				if display_name:
					# Take the current display_name, escape it, and dump it into the "name" field.
					name = re.escape(display_name)
				else:
					# Auto-name the resource in some sort of reasonable and hopefully unique manner.
					name = re.escape(xmlfile.name)

				print name

				# Take the entire text of this file, escape it, and dump it into the "text" field.
				text = re.escape(xmlfile.read())

				# Set hide_info and is_deprecated both = False by default
				hide_info = False
				is_deprecated = False

				# Use the tag type to set the resource_type to html or problem.
				if tag_type == 'html':
					resource_type = 'html'
				elif tag_type == 'problem':
					resource_type = 'problem'
				else:
					resource_type = 'other'
					# (What to do with videos?)

				# If the resource type is problem:
				if resource_type == 'problem':
				
					# Use regex to set problem_type based on whether it's <multiplechoice>, <numericresponse>, <formularesponse>, etc.
					if re.search('<multiplechoice',text):
						problem_type = "multiple_choice"
					elif re.search('<numericalresponse',text):
						problem_type = 'numerical'
					elif re.search('<formularesponse', text):
						problem_type = 'formula'
					elif re.search('<symbolicresponse', text):
						problem_type = 'formula'
					elif re.search('<choiceresponse', text):
						problem_type = 'select_all'
					elif re.search('<custom', text):
						problem_type = 'custom'
					else:
						problem_type = 'other'
				else:
					problem_type = 'not_a_problem'

					# If no problem_type found, go back and set the resource_type to "other"
				# Other required items that we will also need:
					# Learning Objectives!!
					# Description
				# Run the MySQL INSERT command.
				# Link this resource to the current_collection, creating the collection if necessary.
					# (The Collection_Creator function does this just how I want.)

		# Close the file - should be done automatically using the "with open" approach.

	except IOError:
		print 'filepath ' + filepath + ' not associated with file.'


# What if the resource already exists in the database? 
# How to find the appropriate resource? Display_name seems to be all we have.
# May need to have existing resources include a "link to source" field and use those instead.
# Probably need to do a this-to-that table by hand.


####################################################
# Filepath fixer
####################################################

def FixPath(filepath, line):

	# Filepaths as given in edXML files are incorrect. This touches them up.
	# Note that url_name= and filename= paths are treated slightly differently before being sent here.

	if re.search('<html ', line):
		if "problems/" not in filepath and "html/" not in filepath:
			filepath = 'html/' + filepath
		if ".html" not in filepath:
			filepath = filepath + ".html"
	elif re.search('<vertical ', line):
		filepath = 'vertical/' + filepath + '.xml'
	elif re.search('<sequential ', line):
		filepath = 'sequential/' + filepath + '.xml'
	elif re.search('<chapter ', line):
		filepath = 'chapter/' + filepath + '.xml'
	elif re.search('<course ', line):
		filepath = 'course/' + filepath + '.xml'
	
	return filepath


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