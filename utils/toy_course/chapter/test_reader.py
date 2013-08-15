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
		
			# Interpret the file as XML
			xmltree = etree.parse(xmlfile)
			
			# Start with the root of this XML document
			root = xmltree.getroot()
			
			# Print the first tag
			print root[0].tag + ' ' + root.get('display_name')
			
			# Find all the self-closing tags.
			for x in root.iter():
				if not x.text:
					if x.get('display_name'):
						print x.tag + ' ' + x.get('display_name') + ' is self-closing.'
		
		# File closed automatically via "with"

	except IOError:
		print filename + ' not found.'



# Helps with file execution
if __name__ == "__main__":
   main(sys.argv[0:])