from django.db import models
from django.contrib.auth.models import User
from djangosphinx.models import SphinxSearch


class Tag(models.Model):
	text = models.TextField()
	def __unicode__(self): 
		return self.text


class Question(models.Model):
	author = models.ForeignKey(User)
	title = models.CharField(max_length = 60)
	text = models.TextField()
	added = models.DateTimeField(auto_now_add = True, db_index = True)
	tags = models.ManyToManyField(Tag)
	rating = models.IntegerField(default = 0, db_index = True)

	def __unicode__(self): 
		return self.text[:20]

	search = SphinxSearch(weights={
        'title': 100,
        'text': 70,
        'ans_text': 40
    })


class Answer(models.Model):
	author = models.ForeignKey(User)
	question = models.ForeignKey(Question, db_index = True)
	text = models.TextField()
	added = models.DateTimeField(auto_now_add = True, db_index = True)
	is_right = models.BooleanField(default = False, db_index = True)
	rating = models.IntegerField(default = 0, db_index = True)
	def __unicode__(self): 
		return self.text[:20]


class Profile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	rating = models.IntegerField(default = 0)
	avatar = models.ImageField(max_length = 100, upload_to='avatars', 
		default='avatars/empty.gif')
	def __unicode__(self): 
		return self.user.first_name


class Like(models.Model):
	author = models.ForeignKey(User)
	item_type = models.CharField(max_length=10, default='')
	item = models.IntegerField(default=-1)
	added = models.DateTimeField(auto_now_add = True)
	is_like = models.BooleanField(default = True)

	class Meta:
		index_together = ['author', 'item_type', 'item', 'is_like']
