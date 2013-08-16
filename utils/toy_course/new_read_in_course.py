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
import os								# For getting file name
import re								# regular expressions for searching and escaping
import MySQLdb							# python-to-mySQL translator
from collections import OrderedDict		# Ordered dictionary
from lxml import etree					# XML parser


####################################################
# Main takes in arguments, connects to the database, and runs TheOpener.
####################################################
def main(argv):

	# Check for correct usage
	if not argv:
		sys.exit("Please specify an input course.xml file.")
	if len(argv) == 1:
		sys.exit("Usage: python read_in_course.py course.xml")
	if argv[1] == "-h":
		sys.exit("Usage: python read_in_course.py course.xml")

	# Take in a filename from the command line
	filename = str(sys.argv[1])

	# Connect to the database
	db = MySQLdb.connect(host="localhost",
		user="resource_mangler",
		passwd="1l0v3dat3r",
		db="edxresources")

	# Create a Cursor object with which to execute queries
	cur = db.cursor() 
	
	
	containers = OrderedDict([])
	depth = 0
		
	TheOpener(filename, '', filename, containers, depth, cur, db)

	# Clean up the database stuff: Commit all changes, close cursor and database.
	db.commit()
	cur.close()
	db.close()



####################################################
# Reads in files and sends them to the XML Processor or the Resource Muncher
####################################################
def TheOpener(filepath, tag_type, display_name, containers, depth, cur, db):

	# try to open the file, to double-check filepath
	try:
		# If it works, carry on.
		with open(filepath, 'rbU') as trial:
			pass
	except IOError:
		# edX is sloppy with filenames; html and xml may get mixed. Try swapping and/or adding.
		if filepath.endswith('.html'):
			newfilepath = filepath[:len(filepath)-5] + '.xml'
		elif filepath.endswith('xml'):
			newfilepath = filepath[:len(filepath)-4] + '.html'			
		else:
			newfilepath = filepath + '.xml'
		try:
			# If it works, use the new path.
			with open(newfilepath, 'rbU') as trial:
				filepath = newfilepath
		except IOError:
			# File likely doesn't exist. This error will get caught in a minute anyway.
			pass
	
	# open the file for real
	try:
		with open(filepath, 'rbU') as xmlfile:

			# Use the first tag in the file to double-check the display_name. (But not for the first file.)
			if depth > 0:
		
				if root.get('display_name'):
		
					# If the display name doesn't match the current display_name variable, update the variable.
					d_n = root.get('display_name')
					if d_n:
						if d_n != display_name:
							display_name = d_n
							# Remove the existing one if we're going to replace it.
							containers.popitem()
							AddWithoutDuplicates(containers, display_name, root.tag)

				# If an "unknown" display name was passed, and we can't find one here, this file's name should be its actual filename.
				elif 'unknown' in display_name:
					display_name = os.path.basename(xmlfile.name)
					# Remove the existing one if we're going to replace it.
					containers.popitem()
					AddWithoutDuplicates(containers, display_name, root.tag)

			print 'New file: ' + filepath
			
			# Get the text from this file.
			xmltext = xmlfile.read()
			
			# If this file is a resource, send it to the Resource Muncher.
			# Otherwise, it's a container. Send it to the XML processor. 
			if 'html' in tag_type or 'problem' in tag_type:
				ResourceMuncher(xmltext, filepath, tag_type, display_name, containers, depth, cur, db)
			else:
				XMLProcessor(xmltext, filepath, tag_type, display_name, containers, depth, cur, db)

		# Close file - done automatically via "with"
	
	# If no file...
	except IOError:
		print 'filepath ' + filepath + ' not associated with file.'
		# This is not a real item, so remove it from the collection list.
		containers.popitem()


####################################################
# This does the work of examining the XML and traversing it.
####################################################
def XMLProcessor(xmltext, filepath, tag_type, display_name, containers, depth, cur, db):

	# Keep track of how deep we are so we can exit if we're stuck in a loop.
	depth += 1
	if depth > 10:
		sys.exit("Potential infinite loop detected. Exiting. Check for files that reference themselves?")

	# Turn the xml we've been passed into an etree
	root = etree.fromstring(xmltext)
	# print etree.tostring(root, pretty_print=True)
	
	# For every tag in this XML tree:
	for x in root.iter():
	
		# Skip comments.
		if x.tag is not etree.Comment:

			# If this is the kind of tag you built edX courses from...
			if 'course' in x.tag \
				or 'chapter' in x.tag \
				or 'sequential' in x.tag \
				or 'vertical' in x.tag \
				or 'conditional' in x.tag \
				or 'problem' in x.tag \
				or 'html' in x.tag:
		
				print x.tag
	
				# If it's an inline definition, get its info and add it to the container list.
				# Then run this function again with the text inside the container.
				if x.text:
					print '...is an inline container'
					# An inline container has stuff other than whitespace inside the tag.
					if not x.text.strip() == '':
				
						# Get the display_name or say that we don't know it.
						if x.get('display_name'):
							display_name = x.get('display_nme')
						else:
							display_name = 'unknown' + x.tag
						
						# If this is an HTML snippet or a problem defined inline,
						# skip it.
						if 'html' in x.tag or 'problem' in x.tag:
							print 'Skipping inline ' + x.tag + ' item in file  ' +  + '.'
						
						# Add this item to the container dictionary.
						AddWithoutDuplicates(containers, display_name, x.tag)
						
						# Run this routine on the text inside the tag as if it were a file.
						XMLProcessor(x.text, filepath, x.tag, display_name, containers, depth, cur, db)
			
				# If it's a self-closing container (no stuff in tag), attempt to follow the file it links to.
				# We're recursively traversing the file tree.
				else:
			
					print '...is a self-closing container'

					# If this tag has a filename or url_name attribute, use that and go there:
					if x.get('filename') or x.get('url_name'):

						# Get the display_name from this line to pass lower.
						if x.get('display_name'):
							display_name = x.get('display_name')
						else:
							if x.get('filename'):
								display_name = x.get('filename')
							elif x.get('url_name'):
								display_name = x.get('url_name')
							else:
								display_name = 'unknown' + x.tag

						# Need to treat filename="" and url_name="" links slightly differently.

						if x.get('filename'):

							# Get the filepath
							filepath = x.get('filename')

							# Correct the filename - add folder and .xml if needed.
							if x.tag == 'problem':
								if filepath.find("problems/") != 0:
									filepath = 'problems/' + filepath   # Note the s.
								filepath = filepath + '.xml'
							else:
								filepath = FixPath(filepath, x.tag)

						if x.get('url_name'):

							# Get the filepath
							filepath = x.get('url_name')

							# Correct the filepath - swap out colons, add folder and .xml if needed.
							filepath = filepath.replace(':','/')
							if x.tag == 'problem':
								if filepath.find("problem/") != 0:
									filepath = 'problem/' + filepath   # Note the lack of s.
								filepath = filepath + '.xml'
							else:
								filepath = FixPath(filepath, x.tag)

						# Add the file we're headed towards to the list.
						AddWithoutDuplicates(containers, display_name, x.tag)

						# Recursion happens here, but we need to open the file first.
						TheOpener(filepath, x.tag, display_name, containers, depth, cur, db)
						db.commit()

	# Move to next tag (done automatically by the for loop)


####################################################
# This takes in resources and adds them to the database.
####################################################
def ResourceMuncher(xmltext, filepath, tag_type, display_name, containers, depth, cur, db):

	# This page is a resource. Remove its name from the collection list.
	containers.popitem()

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

	# Take the entire text of this file and dump it into the "text" field.
	text = xmltext

	# If the resource type is problem:
	if resource_type == 'problem':
	
		# Use regex to set problem_type based on whether it's <multiplechoice>, <numericresponse>, <formularesponse>, etc.
		if re.search('<multiplechoice', text):
			problem_type = "multiple_choice"
		elif re.search('<numericalresponse', text):
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

		# Get the ID of the resource I just created
		resource_id = cur.lastrowid

		# Link this resource to the current_collection, creating the collection if necessary.
		Collection_Creator(containers, cur, resource_id)

		# Commit the database changes.
		db.commit()


####################################################
# Add something to the collection list and avoid duplicates.
# (Common with single-sequence chapters, e.g. quizzes.)
# Uses lowercase to avoid database case issues.
####################################################

def AddWithoutDuplicates(containers, collection, tag_type):

	for x in containers:
		if x.lower() == collection.lower():
			collection += ' ' + tag_type

	containers[collection] = tag_type


####################################################
# Filepath fixer
####################################################

def FixPath(filepath, tag_type):

	# Filepaths as given in edXML files are incorrect. This touches them up.
	# Note that url_name= and filename= paths are treated slightly differently before being sent here.

	if tag_type == 'html':
		if "problems/" not in filepath and "html/" not in filepath:
			filepath = 'html/' + filepath
		if ".html" not in filepath:
			filepath = filepath + ".html"
	elif tag_type == 'vertical':
		filepath = 'vertical/' + filepath + '.xml'
	elif tag_type == 'sequential':
		filepath = 'sequential/' + filepath + '.xml'
	elif tag_type == 'chapter':
		filepath = 'chapter/' + filepath + '.xml'
	elif tag_type == 'course':
		filepath = 'course/' + filepath + '.xml'
	
	return filepath


####################################################
# Automated Collection Creation!
# Now with Multiple Collections!
####################################################

def Collection_Creator(containers, cur, resource_id):

	added_collections = 0

	for collection in containers:

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
			collection_query += containers[collection] + "', '" 
			collection_query += "0"  + "', '" # is_sequential set to false
			collection_query += "0"  + "', '" # is_deprecated set to false
			collection_query += "2001-01-01" + "')" # creation_date

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