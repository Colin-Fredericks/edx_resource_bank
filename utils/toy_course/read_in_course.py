#!/usr/bin/python

#########
# The goal here is to strip all the text out of an existing edX course and 
#  use it to provide the "text" fields for the resource databse.
# We're traversing the edXML file structure looking for filepaths that end in resources, 
#  going as deep as we need to, and creating resources along the way.
# The general approach is recursive.
#########

#########
# Various concerns:
# What if the resource already exists in the database? 
# How to find the appropriate resource? Display_name seems to be all we have.
# May need to have existing resources include a "link to source" field and use those instead.
# Probably need to do a this-to-that table by hand.
#########


import sys
import os			# For getting file name
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

	# Connect to the database
	db = MySQLdb.connect(host="localhost",
		user="resource_mangler",
		passwd="1l0v3dat3r",
		db="edxresources")

	# Create a Cursor object with which to execute queries
	cur = db.cursor() 
	
	
	collection_list = []
	depth = 0
		
	BigLoop(filename, '', filename, collection_list, depth, cur, db)

	# Clean up the database stuff: Commit all changes, close cursor and database.
	db.commit()
	cur.close()
	db.close()

# This is the recursive function that does most of our work.
def BigLoop(filepath, tag_type, display_name, collection_list, depth, cur, db):

	# Note: The collection_list is being passed by REFERENCE, not by value.
	# We need to manually remove entries.

	if depth > 10:
		sys.exit("Potential infinite loop detected. Exiting. Check for files that reference themselves?")

	# trackers so that we can give some output
	# I just realized these will all need to get passed if we're going to actually use them.
	# linked_objectives = 0 
	added_resources = 0
	added_collections = 0
	filepaths_found = 0
	container_type = []

	# open the file
	try:
		with open(filepath, 'rbU') as xmlfile:

			# Use the first line to double-check the display_name. (But not for the first file.)
			if depth > 0:
				firstline = xmlfile.readline()
				if 'display_name' in firstline:
				
					# If the display name doesn't match the current display_name variable, update the variable.
					d_n = re.search('display_name="(.*?)"', firstline)
					if d_n:
						if d_n != display_name:
							display_name = d_n.group(1)

				# If all else fails, this file's name should be its actual filename.
				elif 'unknown' in display_name:
					display_name = os.path.basename(xmlfile.name)
			
				# Add the current page's name as if it were a collection.
				# We need to remove it when...
				# - returning from an inline container
				# - discovering that this page is a resource
				# We also need to add more collections when running into the appropriate kind of tag, 
				# and remove them when the tag closes.
				collection_list += [display_name]


			# For every line in this file:
			for line in xmlfile:

				# If this line starts an inline container:
				if ('<course' in line or '<chapter' in line or '<sequential' in line or '<vertical' in line) and ('/>' not in line):

					# What kind of collection is this?
					coll_type = re.search('<(\S+)[ >\/]',line).group(1)

					# Get the display_name and add it to the collection list.
					if 'display_name' in line:
						collection_list += [re.search('display_name="(.*?)"', line).group(1)]
					else:
						collection_list += ['unknown ' + coll_type]

					# Avoids duplicating collections (common with exams and other single-sequence chapters)
					if collection_list[len(collection_list)-1] == collection_list[len(collection_list)-2]:
						collection_list[len(collection_list)-1] += ' ' + coll_type

				
				# If this line ends an inline container, remove the last item on the collection list.
				if ('</course>' in line or '</chapter>' in line or '</sequential>' in line or '</vertical>' in line):
					collection_list.pop()
					pass
				
				# If the tag on this line closes on the same line, attempt to open the file it links to 
				# and recursively traverse the file tree.
				# If it's not self-closing, it doesn't actually link to a file. Move on.

				if '/>' in line:

					# If this line has a filename or url_name attribute, use that and go there:
					if 'filename' in line or 'url_name' in line:

						# Get info from the tag for this link.
						tag_type = re.search('<(\S+?) ',line).group(1)

						# Get the display_name from this line to pass lower.
						if 'display_name' in line:
							display_name = re.search('display_name="(.*?)"', line).group(1)
						else:
							if 'filename' in line:
								display_name = re.search('filename="(.*?)"', line).group(1)
							elif 'url_name' in line:
								display_name = re.search('url_name="(.*?)"', line).group(1)
							else:
								display_name = 'unknown collection'

						# Need to treat filename="" and url_name="" links slightly differently.

						if 'filename' in line:

							# Get the filepath
							filepath = re.search('filename="(.*?)"', line).group(1)

							# Correct the filename - add folder and .xml if needed.
							if '<problem ' in line:
								if filepath.find("problems/") != 0:
									filepath = 'problems/' + filepath   # Note the s.
								filepath = filepath + '.xml'
							else:
								filepath = FixPath(filepath, line)

						if 'url_name' in line:

							# Get the filepath
							filepath = re.search('url_name="(.*?)"', line).group(1)

							# Correct the filepath - swap out colons, add folder and .xml if needed.
							filepath = filepath.replace(':','/')
							if '<problem ' in line:
								if filepath.find("problem/") != 0:
									filepath = 'problem/' + filepath   # Note the lack of s.
								filepath = filepath + '.xml'
							else:
								filepath = FixPath(filepath, line)

						# Recursion happens here.
						BigLoop(filepath, tag_type, display_name, collection_list, depth+1, cur, db)
						db.commit()
						
						filepaths_found += 1
						
						
				# Move to next line (done automatically by the for loop)

			# If there are no self-closing tags with filepaths found in this whole file:
			if filepaths_found == 0:

				# This page is a resource. Remove its name from the collection list.
				collection_list.pop()

				# We're going to INSERT a new resource into the database.

				# Use the display_name that was passed (as ammended above) to name this resource.
				# If that name is blank, use the filename.
				if not display_name:
					display_name = os.path.basename(xmlfile.name)
				name = display_name

				# Use the tag type to set the resource_type to html or problem.
				if tag_type == 'html':
					resource_type = 'html'
				elif tag_type == 'problem':
					resource_type = 'problem'
				else:
					resource_type = 'other'
					# (What to do with videos?)

				# Take the entire text of this file, escape it, and dump it into the "text" field.
				with open(filepath, 'rbU') as tempfile:
					text = tempfile.read()

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
						# If none of these tags are found, go back and set the resource_type to "other"
						problem_type = 'other'
				else:
					problem_type = 'not_a_problem'

				# Placeholder values.
				# Note that we'll need to link learning objectives later.
				description = ''
				is_deprecated = '0'		# 0 for false in SQL
				hide_info = '0'			# 0 for false in SQL
				resource_file = ''
				grade_level = ''
				intended_use = ''
				license = ''
				license_link = ''
				license_other_notes = ''
				source = ''
				language = ''
				author = ''
				comments = ''
				creation_date = '2001-01-01'
				solutions_hints_etc = ''


				# Assemble the MySQL INSERT command.
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

				# If this exact resource already exists, skip it.
				if cur.execute(sql_query):
					print "Skipping duplicate entry " + name

				# If it's not a duplicate entry:
				else:

					# Run an "INSERT" command to put in this resource
					sql_start = "INSERT RDB_resource "
					sql_middle = "VALUES ('" 

					sql_query = sql_start + sql_left + sql_middle + sql_right

					cur.execute(sql_query)
					added_resources += 1

					# Get the ID of the resource I just created
					resource_id = cur.lastrowid

					# Link this resource to the current_collection, creating the collection if necessary.

					################
					# Automated Collection Creation!
					# The Collection_Creator function returns the number of new collections that were added. Add 'em up.
					###############

					print 'Linking collections for ' + name
					added_collections += Collection_Creator(collection_list, cur, resource_id)
					db.commit()


		# Close the file -- done automatically via the "with" command

	except IOError:
		print 'filepath ' + filepath + ' not associated with file.'



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
# Now with Multiple Collections!
####################################################

def Collection_Creator(collection_list, cur, resource_id):

	added_collections = 0
	print collection_list

	for collection in collection_list:

		# Check to see if a collection with this name already exists. 
		cur.execute("SELECT id FROM RDB_collection WHERE name = %s", re.escape(collection))

		try:
			# If it does exist, get the id for that collection.
			collection_id = cur.fetchone()[0]
		except TypeError:
			# If it does not exist, say there's no collection with that ID.
			collection_id = False

		# If we don't find it, we're doing to double-check with the unescaped name.
		# I have no idea why this stage is necessary but it is.
		if collection_id == False:
		
			cur.execute("SELECT id FROM RDB_collection WHERE name = %s", collection)

			try:
				# If it does exist, get the id for that collection.
				collection_id = cur.fetchone()[0]
			except TypeError:
				# If it does not exist, say there's no collection with that ID.
				collection_id = False


		# If the collection does not already exist, create it.
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
			collection_query += "0"  + "', '" # is_sequential set to false
			collection_query += "0"  + "', '" # is_deprecated set to false
			collection_query += "2001-01-01" + "')" # creation_date

			print 'Creating collection ' + collection + ' for resource ' + str(resource_id)
			cur.execute(collection_query)
			added_collections += 1
	
			# Get the ID of the collection I just created.
			collection_id = cur.lastrowid
	
		# Link this resource to the collection.
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