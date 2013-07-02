from django.contrib import admin
from RDB.models import Resource
from RDB.models import Learning_Objective
from RDB.models import Learning_Objective_Broad
from RDB.models import Topic
from RDB.models import Keyword
from RDB.models import Analytic
from RDB.models import Analytic_Value
from RDB.models import Custom_Text
from RDB.models import Code_Dependencies
from RDB.models import Collection
from fieldmaker.admin import ExpandableModelAdmin

class Custom_Text_Admin(admin.TabularInline):
	model = Custom_Text
	pass

class Resource_Admin(ExpandableModelAdmin):
	list_filter = ['creation_date','grade_level']
	search_fields = ['name','text']
	readonly_fields = ('creation_date',)

#	fields = ('name', 'resource_type', 'learning_objective', 'hide_info')

	fieldsets = [
		('Required',				{'fields': ['name','resource_type','learning_objective','hide_info']}),
		('Common Items',			{'fields': ['text','topic','keyword','intended_use'], 'classes': ['collapse']}),
		('License and Origin', 		{'fields': ['license','license_link','license_other_notes','source','author','comments'], 'classes': ['collapse']}),
		('For Files',				{'fields': ['resource_file'], 'classes': ['collapse']}),
		('For Problems',			{'fields': ['problem_type'], 'classes': ['collapse']}),
		('For Applications',		{'fields': ['code_dependencies'], 'classes': ['collapse']}),
		('Custom Text',				{'fields': ['analytic'], 'classes': ['collapse']}),
		('Automatically Generated',	{'fields': ['creation_date'], 'classes': ['collapse']}),        
	]
	inlines = [Custom_Text_Admin]
	pass

class Collection_Admin(admin.ModelAdmin):
	list_filter = ['creation_date','collection_type']
	readonly_fields = ('creation_date',)
	
	fieldsets = [
		('Required', 				{'fields': ['name','collection_type','included_resources','is_sequential','learning_objectives_broad','code_dependencies']}),
		('Automatically Generated',	{'fields': ['creation_date'], 'classes': ['collapse']}),        
	]
	pass


admin.site.register(Resource, Resource_Admin)
admin.site.register(Learning_Objective)
admin.site.register(Learning_Objective_Broad)
admin.site.register(Keyword)
admin.site.register(Analytic)
admin.site.register(Analytic_Value)
admin.site.register(Custom_Text)
admin.site.register(Topic)
admin.site.register(Code_Dependencies)
admin.site.register(Collection, Collection_Admin)
