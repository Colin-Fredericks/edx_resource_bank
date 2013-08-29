from django.db import models
from django import forms

class Learning_Objective(models.Model):

	learning_objective = models.CharField(max_length=255)
	short_name = models.CharField(max_length=32)
	def __unicode__(self):
		return self.short_name
	
	class Meta:
		ordering = ('learning_objective',)


class Topic(models.Model):

	topic = models.CharField(max_length=255)
	def __unicode__(self):
		return self.topic
	
	class Meta:
		ordering = ('topic',)


class Keyword(models.Model):

	keyword = models.CharField(max_length=255)
	def __unicode__(self):
		return self.keyword
	
	class Meta:
		ordering = ('keyword',)


class Code_Dependencies(models.Model):
	codebase = models.CharField(max_length=255)
  
	def __unicode__(self):
		return self.codebase

	class Meta:
		ordering = ('codebase',)


class Analytic(models.Model):
	name = models.CharField(max_length=255)
  
	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ('name',)


################### Resource Class ##############################
# This class is The Big Deal. Everything else is tied into this.
#################################################################
class Resource(models.Model):

	# Required items
	name = models.CharField(max_length=255)
	filepath = models.CharField(max_length=255)

	resource_type = models.CharField(max_length=16, choices=(
		('problem', 'problem'), 
		('html', 'html'),
		('plaintext', 'plaintext'), 
		('video', 'video'),
		('audio', 'audio'),
		('image', 'image'),
		('application', 'application'),
		('other', 'other'),
		)
	)
	hide_info = models.BooleanField('Hide info from students?', default=False)
	is_deprecated = models.BooleanField('Is this resource deprecated?', default=False)
#	replace_with = models.IntegerField('Replace with Resource #', blank=True)
#	Replace deprecated resources with a different one by default. Should this point to the resource?

	learning_objective = models.ManyToManyField(Learning_Objective)
	description = models.CharField(max_length=255)


	# Items very likely to be in use
	text = models.TextField(blank=True)	# This is where problems store edXML and most other things store nothing
	keyword = models.ManyToManyField(Keyword, blank=True)
	topic = models.ManyToManyField(Topic, blank=True)
	
	resource_file = models.FileField(upload_to=".", blank=True)

	grade_level = models.CharField(max_length=16, choices=(
		('elementary', 'elementary'), 
		('highschool', 'highschool'),
		('highschool_AP', 'highschool_AP'),
		('college_intro', 'college_intro'), 
		('college', 'college'),
		('graduate', 'graduate'),
		('any', 'any'),
		), default='any'
	)

	intended_use = models.CharField(max_length=16, choices=(
		('class_activity', 'class_activity'), 
		('clicker', 'clicker'),
		('checkpoint', 'checkpoint'),
		('exam', 'exam'),
		('exploration', 'exploration'),
		('homework', 'homework'), 
		('class_prep', 'class_prep'),
		('reference', 'reference'), 
		('test', 'test'),
		('other', 'other'),
		), blank=True
	)

#	needed_resources = # For embedded images and such. Not sure how to do this. Should be extensible.
#	related_resources = # For other related stuff. Not sure how to do this. Should be extensible.
#						# How can we have teachers add suggested related items?
#	All this might be better done using Collections.
	
	
	# License and Origin
	license = models.CharField(max_length=255, blank=True)
	license_link = models.URLField(blank=True)
	license_other_notes = models.TextField(blank=True)
	source = models.CharField(max_length=255, blank=True)
	language = models.CharField(max_length=255, blank=True, default='English')
	author = models.CharField(max_length=255, blank=True)
	comments = models.TextField(blank=True)
	
	# Should be automatically generated
	creation_date = models.DateField(auto_now_add=True)
	
	analytic = models.ManyToManyField(Analytic, blank=True, null=True)	
	
#	
#	file_size = models.IntegerField(blank=True) # measure in Unix standard - bytes? yes?
#												# Should include uploaded file and text, but not other data
#	used_in_courses = same way

	
	# Specifically for problems
#	wrong_answer_responses = # I feel like I need to point to a table for this one.		Check out one-to-many

#	This is too specific to edX's problem types at the moment.
	problem_type = models.CharField(max_length=32, choices=(
		('multiple_choice', 'multiple_choice'), 
		('select_all', 'select_all'), 
		('free_response', 'free_response'),
		('numerical', 'numerical'),
		('formula', 'formula'), 
		('image', 'image'),
		('vector', 'vector'),
		('custom', 'custom'),
		('other', 'other'),
		('not_a_problem', 'not_a_problem'),
		), default='not_a_problem'
	)
	solutions_hints_etc = models.TextField(blank=True)
	
	
#	# Specifically for videos and animations
#	video_length = models.IntegerField(blank=True)	# should be a time, but not a "time of day" kind of time. Like a "4 minutes and 30 seconds" time.
#													# Maybe store in seconds, display in hh:mm:ss?
	
	# Specifically for applications, simulations, etc.
	# Many problems will need this as well, I suppose.
	code_dependencies = models.ManyToManyField(Code_Dependencies, blank=True)
	
	def __unicode__(self):
		return self.name


class Analytic_Value(models.Model):
	analytic = models.ForeignKey(Analytic)
	resource = models.ForeignKey(Resource)
	value = models.FloatField(blank=True)
	note = models.CharField(max_length=255, blank=True)
  
	def __unicode__(self):
		return unicode(self.analytic) + ' = ' + unicode(self.value)


class Custom_Text(models.Model):
	resource = models.ForeignKey(Resource)
	name = models.CharField(max_length=255)
	value = models.CharField(max_length=255,blank=True)

	def __unicode__(self):
		return unicode(self.name) + ' = ' + unicode(self.value)

	class Meta:
		ordering = ('name',)


class Learning_Objective_Broad(models.Model):

	learning_objective = models.CharField(max_length=255)
	short_name = models.CharField(max_length=16)
	def __unicode__(self):
		return self.short_name
	
	class Meta:
		ordering = ('learning_objective',)


class Collection(models.Model):
	# used to collect multiple items, such as a video followed by a problem, or a whole module
	# Should inherit all learning objectives from its members, and also have its own LOs.

	# Required
	name = models.CharField(max_length=255)
	collection_type = models.CharField(max_length=16, choices=(
		('page', 'page'), 
		('module', 'module'), 
		('chapter', 'chapter'),
		('related items', 'related items'),
		('versions', 'versions'),
		('other', 'other'),
		)
	)

	included_resources = models.ManyToManyField(Resource)
	is_sequential = models.BooleanField(default=True)
	is_deprecated = models.BooleanField('Is this resource deprecated?', default=False)

	learning_objectives_broad = models.ManyToManyField(Learning_Objective_Broad)
	# larger-scale, overarching LOs that apply to the collection but are not necessarily obvious from its parts


#	# How do I support randomization? 


	# Optional
	code_dependencies = models.ManyToManyField(Code_Dependencies, blank=True)
	
	# Should be automatically generated
	creation_date = models.DateField(auto_now_add=True)

#	file_size = models.IntegerField() # summed from size of included resources
#	used_in_courses =	# should be a list of every course where this resource has been used... 
						# or do we want to have a "courses" item and draw from that when generating such a list?
						# Need course title, year, and section (if one exists).
	
	def __unicode__(self):
		return self.name



""" Notes
	+ Analytics
		- The specific items would be different for different types of resource
		- make sure this is extendable for future analytics.
		- Hooks for Asset Window (Weightings for learning objectives?)
		- Can we store these by class and by group of students? ("effective for Type X students")

		- IRT difficulty
		- past % correct
		- MIRT skills
		- Gauges
		- Common wrong answers
		- recommendations for next resources
		- etc.


Modules have...
	* Included files...
	* File sequence
	+ Analytics
		- Do analytics for whole modules too.
	+ Collected properties...
		- Show all included learning objectives, all included topics, etc.
	Generated sections (randomly choose 1 of a list or type of problems)


Rejected items:
	used_in_courses: Don't store which courses used a particular item, generate that from the database by interrogating the courses
	used_in_collections: samey-same
	

"""