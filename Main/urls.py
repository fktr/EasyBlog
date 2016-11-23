from django.conf.urls import url
from .views import *

urlpatterns=[
    url(r'^$',IndexView.as_view(),name='index'),
    url(r'^article/(?P<article_id>\d+)/$',ArticleView.as_view(),name='article'),
    url(r'^category/(?P<category_id>\d+)/$',CategoryView.as_view(),name='category'),
    url(r'^tag/(?P<tag_id>\d+)/$',TagView.as_view(),name='tag'),
    url(r'^archive/(?P<year>\d+)/(?P<month>\d+)/$',ArchiveView.as_view(),name='archive'),
    url(r'^search/$',SearchView.as_view(),name='search'),
    url(r'^latest/feed/$',RssFeed(),name='rss'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^chgpwd/$', ChgPwdView.as_view(), name='chgpwd'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^actvuser/(?P<token>\w+.[-_\w]*\w+.[-_\w]*\w+)/$', active_user_view, name='actv_user'),
    url(r'^comment/$',CommentView.as_view(),name='comment'),
]
