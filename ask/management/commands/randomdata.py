from django.core.management.base import BaseCommand
from optparse import make_option

from ask.models import Profile, Question, Answer, Tag, Like
from django.contrib.auth.models import User

from django.db.models import Max, Min

import random, string

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))

class Command(BaseCommand):
    help = 'Generate random data for ask'

    option_list = BaseCommand.option_list + (
        make_option('--users',
            action = 'store',
            dest = 'users',
            default = 0,
        ),
        make_option('--questions',
            action = 'store',
            dest = 'questions',
            default = 0,
        ),
        make_option('--answers',
            action = 'store',
            dest = 'answers',
            default = 0,
        ),
        make_option('--tags',
            action = 'store',
            dest = 'tags',
            default = 0,
        ),
        make_option('--likes',
            action = 'store',
            dest = 'likes',
            default = 1,
        ),
    )

    def handle(self, *args, **options):
#        User.objects.all().delete()
#        Tag.objects.all().delete()
#        Profile.objects.all().delete()
#        Question.objects.all().delete()
#        Answer.objects.all().delete()
#        Like.objects.all().delete()

        try:
            u = User.objects.get(username = 'test')
        except:
            u = User.objects.create(
            username = 'test',
            first_name = 'test',
            email = 'test@aithelle.com')
            u.set_password('test')
            u.save()
            p = Profile.objects.create(
                user_id = u.id, 
                rating = 20)


        item_list = []

        for i in range(0, int(options['users'])):
            u = User(
                username = randomword(9) + str(i), 
                first_name = randomword(3) + str(i), 
                email = randomword(10) + str(i) + '@aithelle.com')
            item_list.append(u)
            if i % 10000 == 0:
                User.objects.bulk_create(item_list)
                item_list = []

        User.objects.bulk_create(item_list)
        um = User.objects.aggregate(Min('id'), Max('id'))

        item_list = []

        for i in range(0, int(options['users'])):
            p = Profile(
                user_id = um['id__max'] - i, 
                rating = random.randint(0, 20))
            item_list.append(p)
            if i % 10000 == 0:
                Profile.objects.bulk_create(item_list)
                item_list = []
        Profile.objects.bulk_create(item_list)
        print 'Users created\n'


        item_list = []
        for i in range(0, int(options['tags'])):
            t = Tag(text = randomword(5))
            item_list.append(t)
            if i % 10000 == 0:
                Tag.objects.bulk_create(item_list)
                item_list = []
        Tag.objects.bulk_create(item_list)

        tm = Tag.objects.aggregate(Min('id'), Max('id'))

        print 'Tags created\n' 

        for i in range(0, int(options['questions'])):
            q = Question(
                author_id = random.randint(um['id__min'], um['id__max']),
                title = randomword(20),
                text = randomword(10) + ' ' + randomword(20),
                rating = random.randint(-100, 100)
                )
            q.save()
            q.tags.add(random.randint(tm['id__min'], tm['id__max']), \
                random.randint(tm['id__min'], tm['id__max']), \
                random.randint(tm['id__min'], tm['id__max']))

        qm = Question.objects.aggregate(Min('id'), Max('id'))

        print 'Questions created\n' 


        item_list = []
        for i in range(0, int(options['answers'])):
            a = Answer(author_id = random.randint(um['id__min'], um['id__max']),
                question_id = random.randint(qm['id__min'], qm['id__max']),
                is_right = random.randint(0,1),
                text = randomword(10) + ' ' + randomword(10),
                rating = random.randint(-100, 100))
            item_list.append(a)
            if i % 10000 == 0:
                Answer.objects.bulk_create(item_list)
                item_list = []

        Answer.objects.bulk_create(item_list)

        am = Answer.objects.aggregate(Min('id'), Max('id'))

        print 'Answers created\n' 


        item_list = []
        for i in range(0, int(options['likes'])):
            item_type = random.choice(['question', 'answer'])
            if item_type == 'question':
                item = random.randint(qm['id__min'], qm['id__max'])
            else:
                item = random.randint(am['id__min'], am['id__max'])
            l = Like(
                author_id = random.randint(um['id__min'], um['id__max']),
                item_type = item_type,
                item = item,
                is_like = random.randint(0, 1)
                )
            item_list.append(l)
            if i % 20000 == 0:
                Like.objects.bulk_create(item_list)
                item_list = []
        Like.objects.bulk_create(item_list)

        print 'Likes created\n' 
