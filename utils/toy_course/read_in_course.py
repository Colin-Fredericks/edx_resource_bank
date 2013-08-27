#!/usr/bin/python

######### The Goals: #########
# Strip all the text out of an existing edX course and use it to 
#  provide the "text" fields for the resource databse.
# We're traversing the edXML file structure looking for filepaths that end in resources, 
#  going as deep as we need to, and creating resources along the way.
# The general approach is recursive.
##############################

######### Various concerns: #########
# What if the resource already exists in the database with minor differences?
# How to find the appropriate resource? Display_name seems to be all we have.
# May need to have existing resources include a "link to source" field and use those instead.
# Probably need to do a this-to-that table by hand.
#####################################


import sys
import os								# For getting file name
import re								# regular expressions for searching and escaping
import mysql.connector					# python-to-mySQL translator
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
	db = mysql.connector.connect(user="resource_mangler",
		passwd="1l0v3dat3r",
		host="localhost",
		database="edxresources",
		buffered=True)

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

	# edX is sloppy with filenames; html and xml may get mixed. 
	# To double-check filepath, try to open the file. Try swapping and/or adding.
	try:
		# If it works, carry on.
		with open(filepath, 'rbU') as trial:
			pass
	except IOError:
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
			# File likely doesn't exist. This error will get caught in the next "try" statement anyway.
			pass
	
	# Open the file for real
	try:
		with open(filepath, 'rbU') as xmlfile:

			# Get the text from this file.
			xmltext = xmlfile.read()
			
			# If this file is a resource, send its text to the Resource Muncher.
			# Otherwise, it's part of the course structure. Send its XML structure to the XML processor. 
			if tag_type == 'html' or tag_type == 'problem':
				ResourceMuncher(xmltext, xmlfile, filepath, tag_type, display_name, containers, depth, cur, db)
			else:
				# Turn the xml into an etree
				try:
					root = etree.fromstring(xmltext)
				except:
					print 'Cannot extract XML. Skipping.'
					return
		
				XMLProcessor(root, xmlfile, filepath, tag_type, display_name, containers, depth, cur, db)

				# Every time we come back from processing XML, pop the last collection.
				try:
					containers.popitem()
				except:
					print 'Done.'
				
		# Close file - done automatically via "with"
	
	# If no file...
	except IOError:
		print 'filepath ' + filepath + ' not associated with file.'
		

####################################################
# This does the work of examining the XML and traversing it.
####################################################
def XMLProcessor(root, xmlfile, filepath, tag_type, display_name, containers, depth, cur, db):

	# Keep track of how deep we are so we can exit if we're stuck in a loop.
	depth += 1
	if depth > 10:
		sys.exit("Potential infinite loop detected. Exiting. Check for files that reference themselves?")

	# Use the root tag for this XML to double-check the current display_name. (But not for the first file.)
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

	# If this is a self-closing tag file, go to the file it links to.
	if len(root) == 0:
		
		# Get the display_name from the current tag, or say that we don't know it.
		if root.get('display_name') is not None:
			display_name = root.get('display_name')
		else:
			display_name = 'unknown ' + root.tag
	
		FollowFilepath(filepath, root.tag, display_name, containers, depth, cur, db, root)
		
	# For every tag in this XML tree:
	for x in root:
	
		# Skip the comments.
		if x.tag is not etree.Comment:
		
			# If this is the kind of tag you built edX courses from...
			if 'course' in x.tag \
				or 'chapter' in x.tag \
				or 'sequential' in x.tag \
				or 'vertical' in x.tag \
				or 'conditional' in x.tag \
				or 'problem' in x.tag \
				or 'html' in x.tag:
		
				# Are there other tags inside this one? If so, it must be an inline definition rather than a link.
				# Get this tag's info and add it to the container list.
				# Then run this function again with the text inside the container.
				if len(x) > 0:

					# Get the display_name from the current tag, or say that we don't know it.
					if x.get('display_name') is not None:
						display_name = x.get('display_name')
					else:
						display_name = 'unknown ' + x.tag
				
					# If this is an HTML snippet or a problem defined inline, skip it.
					# Eventually we might want to keep these, but right now I'm not sure how to name them.
					if 'html' in x.tag or 'problem' in x.tag:
						print 'Skipping inline ' + x.tag + ' item in file  ' + filepath + '.'
				
					# Add this tag to the container dictionary.
					AddWithoutDuplicates(containers, display_name, x.tag)
					
					# Run this routine on the text inside the tag as if it were a file.
					XMLProcessor(x, xmlfile, filepath, x.tag, display_name, containers, depth, cur, db)
					
					# Every time we come back from processing XML, pop the last collection.
					containers.popitem()
				
				# If there are no other tags inside this one, attempt to follow the file it links to.
				else:
				
					FollowFilepath(filepath, x.tag, display_name, containers, depth, cur, db, x)


####################################################
# Fix up the filepath in this tag, and send it to The Opener.
####################################################
def FollowFilepath(filepath, tag_type, display_name, containers, depth, cur, db, XMLtag):

	# If this tag has a filename or url_name attribute, use that and go there:
	if XMLtag.get('filename') or XMLtag.get('url_name'):

		# Get the display_name from this tag to pass lower.
		if XMLtag.get('display_name'):
			display_name = XMLtag.get('display_name')
		else:
			if XMLtag.get('filename'):
				display_name = XMLtag.get('filename')
			elif XMLtag.get('url_name'):
				display_name = XMLtag.get('url_name')
			else:
				display_name = 'unknown ' + XMLtag.tag

		# When creating the filepath, we need to treat filename="" and url_name="" links slightly differently.
		if XMLtag.get('filename'):

			# Get the filepath
			filepath = XMLtag.get('filename')

			# Correct the filepath - add folder and .xml if needed.
			if XMLtag.tag == 'problem':
				if filepath.find("problems/") != 0:
					filepath = 'problems/' + filepath   # Note the s.
				filepath = filepath + '.xml'
			else:
				filepath = FixPath(filepath, XMLtag.tag)

		elif XMLtag.get('url_name'):

			# Get the filepath
			filepath = XMLtag.get('url_name')

			# Correct the filepath - swap out colons, add folder and .xml if needed.
			filepath = filepath.replace(':','/')
			if XMLtag.tag == 'problem':
				if filepath.find("problem/") != 0:
					filepath = 'problem/' + filepath   # Note the lack of s.
				filepath = filepath + '.xml'
			else:
				filepath = FixPath(filepath, XMLtag.tag)

		# Add the file we're headed towards to the list.
		AddWithoutDuplicates(containers, display_name, XMLtag.tag)

		# Open the file.
		TheOpener(filepath, XMLtag.tag, display_name, containers, depth, cur, db)
		
	# If this tag doesn't have a link...
	else:
		print 'False alarm - no link from ' + filepath + ' ' + XMLtag.tag


####################################################
# This takes in resources and adds them to the database.
####################################################
def ResourceMuncher(xmltext, xmlfile, filepath, tag_type, display_name, containers, depth, cur, db):

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
	sql_query = ("SELECT * FROM RDB_resource "
				" WHERE "
				"(name, resource_type, filepath, description, is_deprecated, "
				"hide_info, text, resource_file, grade_level, intended_use, "
				"license, license_link, license_other_notes, source, language, author, "
				"comments, creation_date, problem_type, solutions_hints_etc) "
				" = "
				"(%(name)s, %(resource_type)s, %(filepath)s, %(description)s, %(is_deprecated)s, "
				" %(hide_info)s, %(text)s, %(resource_file)s, %(grade_level)s, %(intended_use)s, "
				" %(license)s, %(license_link)s, %(license_other_notes)s, %(source)s, %(language)s, %(author)s, "
				" %(comments)s, %(creation_date)s, %(problem_type)s, %(solutions_hints_etc)s) ")
	
	sql_data = {
		'name': name,
		'resource_type': resource_type,
		'filepath': filepath,
		'description': description,
		'is_deprecated': is_deprecated,
		'hide_info': hide_info,
		'text': text,
		'resource_file': resource_file,
		'grade_level': grade_level,
		'intended_use': intended_use,
		'license': license,
		'license_link': license_link,
		'license_other_notes': license_other_notes,
		'source': source,
		'language': language,
		'author': author,
		'comments': comments,
		'creation_date': creation_date, 
		'problem_type': problem_type,
		'solutions_hints_etc': solutions_hints_etc,
	}
	
	print sql_query
	print sql_data

	cur.execute(sql_query, sql_data)

	# If this exact resource already exists, skip it.
	if cur.fetchone():
		print "Skipping duplicate entry " + name


	# If it's not a duplicate entry:
	else:

		# Run an "INSERT" command to put in this resource
		sql_insert = ("INSERT INTO RDB_resource "
					"(name, resource_type, filepath, description, is_deprecated, "
					"hide_info, text, resource_file, grade_level, intended_use, "
					"license, license_link, license_other_notes, source, language, author, "
					"comments, creation_date, problem_type, solutions_hints_etc) "
					" VALUES "
					"(%(name)s, %(resource_type)s, %(filepath)s, %(description)s, %(is_deprecated)s, "
					" %(hide_info)s, %(text)s, %(resource_file)s, %(grade_level)s, %(intended_use)s, "
					" %(license)s, %(license_link)s, %(license_other_notes)s, %(source)s, %(language)s, %(author)s, "
					" %(comments)s, %(creation_date)s, %(problem_type)s, %(solutions_hints_etc)s) ")

		cur.execute(sql_insert, sql_data)

		# Get the ID of the resource I just created
		resource_id = cur.lastrowid

		# Link this resource to the current_collection, creating the collection if necessary.
		Collection_Creator(containers, cur, resource_id, display_name)

		# Commit the database changes.
		db.commit()


####################################################
# Add something to the collection list and avoid duplicates.
# (Common with single-sequence chapters, e.g. quizzes.)
# Uses lowercase to avoid database case issues.
####################################################
def AddWithoutDuplicates(containers, collection, tag_type):

	for x in containers:
		# If the name of the collection matches, add the type of collection to the name.
		if containers[x].lower() == collection.lower():
			collection += ' ' + tag_type
		# If the type of this collection is the same as an existing one, remove the old one.
		if x == tag_type:
			containers.popitem()

	containers[tag_type] = collection


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
def Collection_Creator(containers, cur, resource_id, display_name):

	added_collections = 0

	for collection in containers:

		# Check to see if a collection with this name already exists. 
		cur.execute("SELECT id FROM RDB_collection WHERE name = %s", (containers[collection],))

		try:
			# If it does exist, get the id for that collection.
			collection_id = cur.fetchone()
		except TypeError:
			# If it does not exist, say there's no collection with that ID.
			collection_id = False
		
		# If we don't find it, we're doing to double-check with the escaped name.
		# I have no idea why this stage is necessary but it is.
		if collection_id == False:
		
			cur.execute("SELECT id FROM RDB_collection WHERE name = %s", (re.escape(containers[collection]),))

			try:
				# If it does exist, get the id for that collection.
				collection_id = cur.fetchone()
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

			collection_query += containers[collection] + "', '" 
			collection_query += collection + "', '" 
			collection_query += "1"  + "', '" # is_sequential set to true
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

		try:
			cur.execute(resource_insert_query)
		except:
			print 'Duplicate entry: "' + display_name + '" in collection "' + containers[collection] + '". Not added.'
		added_collections += 1

		

	return added_collections


# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])