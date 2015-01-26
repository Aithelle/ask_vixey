from django.core.management.base import BaseCommand
from ask.models import Profile, Question, Answer, User
from django.core.cache import caches

memcached = caches['default']

class Command(BaseCommand):
	help = 'init memcached for best users'

	def handle(self, *args, **options):
		profiles = Profile.objects.only('user__id').select_related('user__id')
		for profile in profiles:
			good_questions = Question.objects.filter(author = profile.user.id, rating__gt = 0).count()
			bad_questions = Question.objects.filter(author = profile.user.id, rating__lt = 0).count()
			good_answers = Answer.objects.filter(author = profile.user.id, rating__gt = 0).count()
			bad_answers = Answer.objects.filter(author = profile.user.id, rating__lt = 0).count()
			profile.rating = 3 * good_questions + good_answers - bad_questions - 2 * bad_answers
			profile.save()
		result = User.objects.order_by('-profile__rating').only('username').values()[:10]
		memcached.set('best_users', result, 60*60*24*14)