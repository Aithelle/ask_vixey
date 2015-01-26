from django.core.management.base import BaseCommand
from django.core.cache import caches
from django.db.models import Count
from ask.models import Tag

memcached = caches['default']
class Command(BaseCommand):
	help = 'init memcached for popular tags'

	def handle(self, *args, **options):
		tags = Tag.objects.exclude(text = '').\
			annotate(num_quests = Count('question')).order_by('-num_quests').values()[:30]
		memcached.set('popular_tags', tags, 60*60*24*14)