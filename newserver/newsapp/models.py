from django.db import models

# Create your models here.
from django.contrib import admin
from django.db import models
# Create your models here.
class Account(models.Model):
	username = models.CharField(max_length=50)
	password = models.CharField(max_length=50)
	content = models.CharField(max_length=500,default="")
	email = models.CharField(max_length=50,default="")
	phone = models.CharField(max_length=50,default="")
	isadministrator = models.CharField(max_length=50,default="0")
	def __unicode__(self):
		return self.name
class UserAdmin(admin.ModelAdmin):
	list_display = ('username','password','content','email','phone','isadministrator')
admin.site.register(Account,UserAdmin)
