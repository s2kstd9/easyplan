from django.contrib import admin
from .models import User, Subject, Item, Scope, LearningPlanList, TimeTableList, TimeTable

admin.site.register(User)
admin.site.register(Subject)
admin.site.register(Item)
admin.site.register(Scope)
admin.site.register(LearningPlanList)
admin.site.register(TimeTableList)
admin.site.register(TimeTable)
