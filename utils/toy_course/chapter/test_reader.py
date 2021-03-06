#!/usr/bin/python

# This is just me trying out the XML parser.

import sys
from lxml import etree

def main(argv):

	# Check for correct usage
	if not argv:
		sys.exit("Please specify an input file.")
	if len(argv) == 1:
		sys.exit("Usage: python test_reader.py whatever.csv")
	if argv[1] == "-h":
		sys.exit("Usage: python test_reader.py whatever.csv")

	# Take in a filename from the command line
	filename = str(sys.argv[1])

	try:
		# Open the file
		with open(filename, 'rbU') as xmlfile:
		
			xmltext = xmlfile.read()
		
			TheLoop(xmltext)
		
		# File closed automatically via "with"

	except IOError:
		print filename + ' not found.'


def TheLoop(xmltext):

	# Turn the xml we've been passed into an etree
	root = etree.fromstring(xmltext)
	
	# prints all the tags in the file.
	# for x in root.iter():
	#	print x.tag + ' ' + str(x.attrib)
	
	# Prints whole file
	# print etree.tostring(root, pretty_print=True)
	
	# prints the fist five tags in the file.
	"""
	print root.tag
	print root[0].tag + ' ' + str(root[0].attrib)
	print root[1].tag + ' ' + str(root[1].attrib)
	print root[2].tag + ' ' + str(root[2].attrib)
	print root[3].tag + ' ' + str(root[3].attrib)
	"""
	
	# How many items in this tree?
	# print len(root)
	
	# How many items in each part of the tree?
	for x in root:
		print x.tag + ' ' + str(x.attrib)
		print len(x)



# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])