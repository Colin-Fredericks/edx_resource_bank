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
	
	print etree.tostring(root, pretty_print=True)




# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])