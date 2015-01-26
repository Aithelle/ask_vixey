from django.conf.urls import patterns, url, include

from ask import views

urlpatterns = patterns('',
    url(r'^helloworld/$', views.helloworld, name='helloworld'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^login$', views.signin, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^settings$', views.settings, name='settings'),
    url(r'^question/(?P<quest_id>\d+)/$', views.question, name='question'),
    url(r'^tag/(?P<tag_id>\d+)/$', views.tag, name='tag'),
    url(r'^ask$', views.ask, name='ask'),
    url(r'^answer/(?P<quest_id>\d+)/$', views.answer, name='answer'),
    url(r'^tick$', views.tick, name='tick'),
    url(r'^vote$', views.vote, name='vote'),
    url(r'^search$', views.search, name='search'),
    url(r'^$', views.index, name='index'),
)

import debug_toolbar
urlpatterns += patterns('',
    url(r'^__debug__/', include(debug_toolbar.urls)),
)