from django.db import models
from django import forms
from fieldmaker.forms import ExpandableForm, ExpandableModelForm


class Learning_Objective(models.Model):

	learning_objective = models.CharField(max_length=255)
	short_name = models.CharField(max_length=16)
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


# class Analytic(models.Model):
# 	name = models.CharField(max_length=255)
# 	value = models.FloatField(blank=True)
#   
# 	def __unicode__(self):
# 		return unicode(self.name) + ' = ' + unicode(self.value)
# 
# 	class Meta:
# 		ordering = ('name',)
# 
# class Custom_Text(models.Model):
# 	name = models.CharField(max_length=255)
# 	value = models.CharField(max_length=255,blank=True)
# 
# 	def __unicode__(self):
# 		return unicode(self.name) + ' = ' + unicode(self.value)
# 
# 	class Meta:
# 		ordering = ('name',)
#
# class Custom_Text_Value(models.Model):
# 	name = models.ForeignKey(Custom_Text)
# 	def __unicode__(self):
# 		return unicode(self.name) + ' = ' + unicode(self.value)

class Analytic(models.Model):
	name = models.CharField(max_length=255)
  
	def __unicode__(self):
		return self.name

	class Meta:
		ordering = ('name',)

class Resource(models.Model):

	# Required items
	name = models.CharField(max_length=255)

	resource_type = models.CharField(max_length=16, choices=(
		('problem', 'problem'), 
		('html', 'html'),
		('plaintext', 'plaintext'), 
		('video', 'video'),
		('audio', 'audio'),
		('image', 'image'),
		('application', 'application'),
		)
	)
	hide_info = models.BooleanField('Hide info from students?', default=False)

	learning_objective = models.ManyToManyField(Learning_Objective)


	# Items very likely to be in use
 	text = models.TextField(blank=True)	# This is where problems store edXML and most other things store nothing
 	keyword = models.ManyToManyField(Keyword, blank=True)
 	topic = models.ManyToManyField(Topic, blank=True)


	custom_text = models.CharField(max_length=255, blank=True)
	custom_text_value = models.CharField(max_length=255, blank=True)
	# This is the worst, least extensible way to do custom entries.
	# Even as a last resort it would not be worth doing.

	
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
		('exploration', 'exploration'),
		('class_activity', 'class_activity'), 
		('clicker', 'clicker'),
		('checkpoint', 'checkpoint'),
		('homework', 'homework'), 
		('test', 'test'),
		('reference', 'reference'), 
		('exam', 'exam'),
		('other', 'other'),
		), blank=True
	)
#
# 	needed_resources = # For embedded images and such. Not sure how to do this. Should be extensible.
# 	related_resources = # For other related stuff. Not sure how to do this. Should be extensible.
# 						# How can we have teachers add suggested related items?


	# License and Origin
 	license = models.CharField(max_length=255, blank=True)
 	license_link = models.URLField(blank=True)
 	license_other_notes = models.TextField(blank=True)
 	source = models.CharField(max_length=255, blank=True)
 	author = models.CharField(max_length=255, blank=True)
 	comments = models.TextField(blank=True)
	
	

	# Should be automatically generated
	creation_date = models.DateField(auto_now_add=True)
	
	analytic = models.ManyToManyField(Analytic, blank=True, null=True)
	# This version stores the data correctly, exactly how I want it. 
	# People can define new analytics, 
	# There is a value out there associated with both the model and the particular analytic in question.
	# Unfortunately, it's very difficult to edit.
	
	
	
#	
#	file_size = models.IntegerField(blank=True) # measure in Unix standard - bytes? yes?
#												# Should include uploaded file and text, but not other data
#	used_in_courses = same way

	
	# Specifically for problems
#	wrong_answer_responses = # I feel like I need to point to a table for this one.		Check out one-to-many
 	problem_type = models.CharField(max_length=16, choices=(
 		('multiple_choice', 'multiple_choice'), 
 		('select_all', 'select_all'), 
 		('free_response', 'free_response'),
 		('numerical', 'numerical'),
 		('formula', 'formula'), 
 		('image', 'image'),
 		('vector', 'vector'),
 		('custom', 'custom'),
 		('not_a_problem', 'not_a_problem'),
 		), default='not_a_problem'
 	)
 
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
  
	def __unicode__(self):
		return unicode(self.analytic) + ' = ' + unicode(self.value)


class MyForm(ExpandableForm):
	# This maybe allows the creation of new custom entries.
	title = forms.CharField()

	class Meta:
		form_key = 'myform'

class MyModelForm(ExpandableModelForm):
	# This... I have no idea. I think it associates my custom stuff with the Resource model?
    class Meta:
        model = Resource
        form_key = 'resource'


class Collection(models.Model):
	# used to collect multiple items, such as a video followed by a problem, or a whole module
	# Should inherit all learning objectives from its members, and also have its own LOs.

	# Required
	name = models.CharField(max_length=255)
	collection_level = models.CharField(max_length=16, choices=(
		('page', 'page'), 
		('module', 'module'), 
		('chapter', 'chapter'),
		)
	)
#	included_resources = 	# Should be several links to Resources or sub-Collections, in order		many-to-many
#							# How do I support randomization? 
	is_sequential = models.BooleanField(default=True)

#	learning_objectives_overall = # larger-scale, overarching LOs that apply to the collection but are not necessarily obvious from its parts

	# Optional
#	code_dependecies =  # Should be several strings

	# Should be automatically generated
#	creation_date = models.DateField()
#	file_size = models.IntegerField() # summed from size of included resources
#	learning_objectives = # should be automatically generated from included resources
#	topics = # should be automatically generated from included resources
#	keywords = # should be automatically generated from included resources
#	used_in_courses = 	# should be a list of every course where this resource has been used... 
						# or do we want to have a "courses" item and draw from that when generating such a list?
						# Need course title, year, and section (if one exists).
#	used_in_collections = # same deal
#	analytics = # Yeah, *really* not sure how to do this one.
	
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