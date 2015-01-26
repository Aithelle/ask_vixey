from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages, auth
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from os import path, remove
from ask.models import *
from ask.forms import *
from django.db.models import Count


@require_http_methods(["GET", "POST"])
def helloworld(request):
    getsItems = request.GET.lists()
    putsItems = request.POST.lists()
    context = {'getsItems' : getsItems, 'putsItems' : putsItems}
    return render(request, 'ask/helloworld.html', context)


@require_http_methods(["GET"])
def index(request):
    back = request.path
    sort = request.GET.get('sort', '')
    quest_list = Question.objects.select_related('author__id', 'author__profile__avatar_url').\
    prefetch_related('tags')
    if sort == 'rating':
        quest_list = quest_list.order_by('-rating')
        back += "?sort=rating"
    else:
        quest_list = quest_list.order_by('-added')

    paginator = Paginator(quest_list, 20)
    page = request.GET.get('page')
    try:
        items_list = paginator.page(page)
    except PageNotAnInteger:
        items_list = paginator.page(1)
    except EmptyPage:
        items_list = paginator.page(paginator.num_pages)
    context = {'items_list': items_list, 'sort': sort, 'back': back}
    return render(request, 'ask/index.html', context)


@require_http_methods(["GET"])
def search(request):
    back = request.path
    query = request.GET.get('query', '')

    quest_list = Question.search.query(query).order_by('-@weight') #.select_related('author__id', 'author__profile__avatar_url')

    paginator = Paginator(quest_list, 20)
    page = request.GET.get('page')
    try:
        items_list = paginator.page(page)
    except PageNotAnInteger:
        items_list = paginator.page(1)
    except EmptyPage:
        items_list = paginator.page(paginator.num_pages)
    context = {'items_list': items_list, 'back': back, 'highlight': query}
    return render(request, 'ask/search.html', context)


@require_http_methods(["GET"])
def tag(request, tag_id):
    tag = get_object_or_404(Tag, id = tag_id)
    quest_list = tag.question_set.all().select_related('author__id', 'author__profile__avatar_url').\
    prefetch_related('tags').annotate(answer_count = Count('answer')).order_by('-rating')
    paginator = Paginator(quest_list, 20)
    page = request.GET.get('page')
    try:
        items_list = paginator.page(page)
    except PageNotAnInteger:
        items_list = paginator.page(1)
    except EmptyPage:
        items_list = paginator.page(paginator.num_pages)
    context = {'tag': tag, 'items_list': items_list, 'back': request.path}
    return render(request, 'ask/tag.html', context)


@require_http_methods(["GET"])
def question(request, quest_id):
    question = get_object_or_404(Question.objects.select_related('author__id', 'author__profile__avatar_url').\
    prefetch_related('tags').annotate(answer_count = Count('answer')), id = quest_id)
    highlight = request.GET.get('highlight', '')

    answer_list = Answer.objects.filter(question = quest_id).select_related('author__id', 'author__profile__avatar_url', 'question__author_id').order_by('-is_right', '-added') 
    paginator = Paginator(answer_list, 30)
    page = request.GET.get('page')
    try:
        page_list = paginator.page(page)
    except PageNotAnInteger:
        page_list = paginator.page(1)
    except EmptyPage:
        page_list = paginator.page(paginator.num_pages)
    context = {'question': question, 'items_list': page_list, 'back': request.path, 'highlight': highlight}
    return render(request, 'ask/question.html', context)


@require_http_methods(["GET"])
def logout(request):
    back = request.GET.get('back', '/')

    if request.user.is_authenticated():
        auth.logout(request)
        messages.success(request, "Successfully logged out!")
    else:
        messages.warning(request, "You've already logged out")
    return redirect(back)


@require_http_methods(["GET", "POST"])
def signin(request):
    back = request.GET.get('back', '/')

    if request.method == 'POST':
        if request.user.is_authenticated():
            auth.logout(request)

        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(username = form.cleaned_data['login'], 
                password = form.cleaned_data['password'])
            if user is not None and user.is_active:
                try:
                    user.profile
                except Profile.DoesNotExist:
                    profile = Profile(user = user, avatar='avatars/empty.gif')
                    profile.save()

                auth.login(request, user)
                messages.success(request, "Successfully logged in")
                
                return redirect(back)

            messages.error(request, "Sorry, wrong login or password", extra_tags='alert-danger')
    
    if request.method == 'GET':
        if request.user.is_authenticated():
            messages.warning(request, "You've already logged in")

    context = {'back': back}
    return render(request, 'ask/login.html', context)


@require_http_methods(["GET", "POST"])
def ask(request):
    back = request.GET.get('back', '/')
    context = {'back': back}

    if not request.user.is_authenticated():
        messages.warning(request, "You need to log in to ask. Please log in and try again")
        return redirect('/login?back=ask')

    if request.method == 'POST':
        form = AskForm(request.POST)
        if form.is_valid():
            q = Question(title = form.cleaned_data['title'], 
                text = form.cleaned_data['text'], 
                author = User.objects.get(id = request.user.id))
            q.save()

            tags = form.cleaned_data['tags']
            
            for t in tags.split(', '):
                try:
                    tag = Tag.objects.get(text = t)
                except Tag.DoesNotExist:
                    tag = Tag(text = t)
                    tag.save()
                q.tags.add(tag)
            
            q.save()
            
            messages.success(request, "Successfully asked!")
            return redirect('/question/' + str(q.id))

        else:
            for k, v in form.errors.items():
                for e in v:
                    messages.error(request, e, extra_tags='alert-danger')

    return render(request, 'ask/ask.html', context)


@require_http_methods(["POST", "GET"])
def answer(request, quest_id):
    back = request.GET.get('back', '/')
    context = {'back': back}

    if not request.user.is_authenticated():
        messages.error(request, 
            "You need to log in to answer. Please log in and try again",
            extra_tags='alert-danger')
        return redirect('/login?back=/question/' + str(quest_id))

    question = get_object_or_404(Question.objects.only('id', 'title'), id = quest_id)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            a = Answer(text = form.cleaned_data['text'],
                question = question, 
                author = User.objects.get(id = request.user.id))
            a.save()
            
            question_url = '/question/' + str(quest_id) + '/#answer' + str(a.id)
            send_mail('Your question has been answered', \
                'Cheers from Ask Vixey!\nYour question ' + question.title + \
                ' has got an answer. Here is a link for it: http://ask.aithelle.com' + \
                question_url, 'postbot@aithelle.com', [question.author.email])

            messages.success(request, "Successfully answered!")
            return redirect(question_url)

        for k, v in form.errors.items():
            for e in v:
                messages.error(request, e, extra_tags='alert-danger') 

    return redirect('/question/' + str(quest_id))


@require_http_methods(["GET", "POST"])
def signup(request):
    back = request.GET.get('back', '/')
    context = {'back': back}

    if request.method == "GET":
        if request.user.is_authenticated():
            messages.warning(request, "You've already been registered")
            return redirect(back)
        return render(request, 'ask/signup.html', context)

    form = SignUpForm(request.POST)

    if form.is_valid():
        if request.user.is_authenticated():
            auth.logout(request)

        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        email = form.cleaned_data['email']
        nickname = form.cleaned_data['nickname']

        user = User.objects.create_user(username, email, password, 
            first_name = nickname)
        user.save()

        profile = Profile(user = user)

        avatar = request.FILES.get('avatar', '')
        if avatar is not '':
            name, ext = path.splitext(avatar.name)
            avatar.name = str(user.id) + ext
            profile.avatar = avatar

        profile.save()

        messages.success(request, "Successfully registered. You can log in now")
        return redirect(back)

    for k, v in form.errors.items():
        for e in v:
            messages.error(request, e, extra_tags='alert-danger')
 
    return render(request, 'ask/signup.html', context)


@require_http_methods(["GET", "POST"])
def settings(request):
    if not request.user.is_authenticated():
        messages.error(request, 
            "You need to log in to change settings. Please log in and try again",
            extra_tags='alert-danger')
        return redirect('/login?back=/settings')


    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES)
        if not form.is_valid():
            for k, v in form.errors.items():
                for e in v:
                    messages.error(request, e, extra_tags='alert-danger')
            redirect("/settings")
        else:
            new_login = form.cleaned_data['login']
            changes = False
            if new_login != request.user.username:
                if User.objects.filter(username = new_login).exists():
                    messages.error(request, "Login already exists", extra_tags='alert-danger')
                else:
                    request.user.login = new_login
                    changes = True

            new_email = form.cleaned_data['email']
            if new_email != request.user.email:
                if User.objects.filter(email = new_email).exists():
                    messages.error(request, "Email already exists", extra_tags='alert-danger')
                else:
                    request.user.email = new_email
                    changes = True

            new_nickname = form.cleaned_data['nickname']
            if new_nickname != request.user.first_name:
                if User.objects.filter(first_name = new_nickname).exists():
                    messages.error(request, "Nickname already exists", extra_tags='alert-danger')
                else:
                    request.user.first_name = new_nickname
                    changes = True

            new_avatar = request.FILES.get('avatar', '')
            if new_avatar is not '':
                if request.user.profile.avatar:
                    if request.user.profile.avatar != 'avatars/empty.gif' and \
                        path.isfile(request.user.profile.avatar.path):
                        remove(request.user.profile.avatar.path) 
                request.user.profile.avatar = new_avatar
                request.user.profile.save()

            if changes == True:
                request.user.save()

            messages.success(request, "Settings saved")

    return render(request, 'ask/settings.html', {})


@require_http_methods(["GET"])
def tick(request):
    back = request.GET.get('back', '/')
    context = {'back': back}

    answerid = request.GET.get('answer', '')
    if answerid == '':
        messages.warning(request, "Nothing to mark")
        return redirect(back)

    ticked = get_object_or_404(Answer.objects.only('id', 'is_right'), id = answerid)

    if not request.user.is_authenticated():
        messages.error(request, 
            "You need to log in to mark answers. Please log in and try again",
            extra_tags='alert-danger')
        return redirect('/login?back=' + back)

    if request.user != ticked.question.author:
        messages.warning(request, "You can mark only your own question answers")
        return redirect(back)

    if ticked.is_right == True:
        ticked.is_right = False
        messages.success(request, "Successfully unmarked answer as right!")
        ticked.save()

    else:
        if not Answer.objects.filter(question = ticked.question, is_right = True).exists():
            ticked.is_right = True
            messages.success(request, "Successfully marked answer as right!")
            ticked.save()
        else:
            messages.warning(request, 
            "You can mark only one answer as correct. Please unmark the other one and try again")

    return redirect(back)

@require_http_methods(["GET"])
def vote(request):
    back = request.GET.get('back', '/')
    context = {'back': back}

    if not request.user.is_authenticated():
        messages.error(request, 
            "You need to log in to vote. Please log in and try again",
            extra_tags='alert-danger')
        return redirect('/login?back=' + back)

    item_type = request.GET.get('type', '')
    item_id = request.GET.get('id', '')
    is_like = int(request.GET.get('like', ''))

    if not (item_type in ['answer', 'question']) or item_id == '' or not (is_like in [True, False]):
        messages.error(request, "Wrong vote information", extra_tags='alert-danger')
        return redirect(back)

    like = Like(author = request.user, item_type = item_type, item = item_id, is_like = is_like)

    if item_type == 'question':
        item = get_object_or_404(Question, id = item_id)
    else:
        item = get_object_or_404(Answer, id = item_id)

    if request.user == item.author:
        essages.error(request, 
            "You can't vote for yourself", extra_tags='alert-danger')
        return redirect(back)

    like_count = Like.objects.filter(author = request.user, item_type = item_type, 
        item = item_id, is_like = 1).count()

    dislike_count = Like.objects.filter(author = request.user, item_type = item_type, 
        item = item_id, is_like = 0).count()

    result = like_count - dislike_count

    if result < -1 or result > 1:
        messages.error(request, 
            "Something is wring with your vote history. Please contact administrator", extra_tags='alert-danger')
        return redirect(back)

    if result >= 0 and like.is_like == 0:
        item.rating -= 1
    
    else:
        if result <= 0 and like.is_like == 1:
            item.rating += 1
        else:
            messages.warning(request, 
            "You can't vote twice, but you can undo your vote and vote again")
            return redirect(back)

    item.save()
    like.save()

    messages.success(request, 
            "Your vote was considered! You can undo it at any moment")

    return redirect(back)