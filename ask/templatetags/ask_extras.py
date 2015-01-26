from django import template
from django.core.cache import caches
from django.utils.safestring import mark_safe
from ask.models import *

register = template.Library()
memcached = caches['default']

@register.filter
def highlight(text, word):
    return mark_safe(text.replace(word, "<span class='highlight'>%s</span>" % word))

@register.inclusion_tag('ask/best_users.html')
def best_users():
	users = memcached.get('best_users')
	return {'users': users}

@register.inclusion_tag('ask/popular_tags.html')
def popular_tags():
	tags = memcached.get('popular_tags')
	return {'tags': tags}