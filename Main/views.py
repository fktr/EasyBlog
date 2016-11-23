from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView,DetailView
from django.views.generic.edit import FormView
from django.db.models import Q
from django.db.models.signals import post_save
from django.contrib.syndication.views import Feed
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from .models import Article,Category,Tag,Account,Comment
from .forms import LoginForm,RegisterForm,ChgPwdForm,CommentForm
from .signature import token_confirm,settings

# Create your views here.
class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        article_list=Article.objects.filter(status='p')
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(IndexView,self).get_context_data(**kwargs)

class ArticleView(DetailView):
    model = Article
    template_name = 'detail.html'
    context_object_name = 'article'
    pk_url_kwarg = 'article_id'

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        kwargs['comment_list']=self.object.comment_set.all()
        kwargs['form']=CommentForm()
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(ArticleView,self).get_context_data(**kwargs)

class CategoryView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        article_list=Article.objects.filter(category=self.kwargs['category_id'],status='p')
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(CategoryView,self).get_context_data(**kwargs)

class TagView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        article_list=Article.objects.filter(tag=self.kwargs['tag_id'],status='p')
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(TagView,self).get_context_data(**kwargs)

class ArchiveView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        article_list=Article.objects.filter(created_time__year=self.kwargs['year'],
                                            created_time__month=self.kwargs['month'],status='p')
        return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(ArchiveView,self).get_context_data(**kwargs)

class SearchView(ListView):
    template_name = 'index.html'
    context_object_name = 'article_list'

    def get_queryset(self):
        if 's' in self.request.GET:
            s=self.request.GET['s']
            if s:
                article_list=Article.objects.filter(Q(title__contains=s)|Q(category__name__contains=s)
                |Q(tag__name__contains=s)|Q(body__contains=s)|Q(abstract__contains=s)
                |Q(comment__body__contains=s),Q(status='p'))
                article_list=list(set(article_list))
                return article_list
            article_list=Article.objects.filter(status='p')
            return article_list

    def get_context_data(self, **kwargs):
        kwargs['category_list']=Category.objects.all().order_by('name')
        kwargs['tag_list']=Tag.objects.all().order_by('name')
        kwargs['date_archive']=Article.objects.archive()
        if 's' in self.request.GET:
            kwargs['search']=True
            kwargs['s']=self.request.GET['s']
        if self.request.user.is_anonymous():
            kwargs['user']=False
        else:
            kwargs['user']=self.request.user.username
        return super(SearchView,self).get_context_data(**kwargs)

class RssFeed(Feed):
    title="F.H.J's Blog"
    link='/latest/feed/'
    description='Six Newest Articles of F.H.J'

    def items(self):
        return Article.objects.order_by('-last_modified_time')[:6]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.abstract

    def item_pubdate(self,item):
        return item.last_modified_time

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def form_valid(self, form):
        username=form.cleaned_data['username']
        password=form.cleaned_data['password']
        user=authenticate(username=username,password=password)
        if user is not None and user.is_active:
            login(self.request,user)
            msg='登陆成功'
            url=reverse('Main:index')
        else:
            msg='登录无效,请确认已注册激活并输入正确密码'
            url=reverse('Main:login')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm

    def form_valid(self, form):
        username=form.cleaned_data['username']
        email=form.cleaned_data['email']
        password=form.cleaned_data['password']
        user=User.objects.filter(username=username)
        if len(user)!=0:
            msg='该用户名已存在,请尝试其他用户名注册'
            url=reverse('Main:register')
        else:
            user=User.objects.create_user(username,email,password)
            user.is_active=False
            user.save()
            token=token_confirm.generate_validate_token(username)
            html_cont = '<p>%s,你好！欢迎来到F.H.J的博客!请于一小时之内<a href="%s">点此链接</a>完成验证.</p>' % (username,
            '/'.join([settings.DOMAIN,'actvuser', token]))
            message=EmailMultiAlternatives('用户注册验证信息',html_cont,settings.EMAIL_HOST_USER,[email])
            message.attach_alternative(html_cont,'text/html')
            message.send()
            msg='请检查您的邮箱信息,并于一小时之内激活验证'
            url=reverse('Main:index')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

def active_user_view(request,token):
    try:
        username=token_confirm.confirm_validate_token(token)
    except:
        username=token_confirm.remove_validate_token(token)
        users=User.objects.filter(username=username)
        for user in users:
            user.delete()
        msg='对不起,验证链接已经过期,请重新注册'
        url=reverse('Main:register')
        data={'message':msg,'url':url}
        return render(request, 'message.html', data)
    try:
        user=User.objects.get(username=username)
    except User.DoesNotExist:
        msg='对不起,你所验证的用户不存在,请重新注册'
        url=reverse('Main:register')
        data={'message':msg,'url':url}
        return render(request, 'message.html', data)
    user.is_active=True
    user.save()
    msg='验证成功'
    url=reverse('Main:login')
    data={'message':msg,'url':url}
    return render(request, 'message.html', data)

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    msg='退出登录'
    url=reverse('Main:index')
    data={'message':msg,'url':url}
    return render(request, 'message.html', data)

class ChgPwdView(FormView):
    template_name = 'chgpwd.html'
    form_class = ChgPwdForm

    def form_valid(self, form):
        if  not self.request.user.is_authenticated():
            msg='您还没有登录'
            url=reverse('Main:login')
        else:
            username=self.request.user.username
            old_password=form.cleaned_data['old_password']
            new_password=form.cleaned_data['new_password']
            user=authenticate(username=username,password=old_password)
            if user is None:
                msg='旧密码输入错误'
                url=reverse('Main:chgpwd')
            else:
                user.set_password(new_password)
                user.save()
                msg='修改密码成功'
                url=reverse('Main:login')
        data={'message':msg,'url':url}
        return render(self.request, 'message.html', data)

@receiver(post_save,sender=User)
def create_account(sender,**kwargs):
    if kwargs.get('created'):
        Account.objects.get_or_create(user=kwargs.get('instance'))

class CommentView(FormView):
    template_name = 'detail.html'
    form_class = CommentForm

    def form_valid(self, form):
        article = get_object_or_404(Article, pk=self.request.POST['article_id'])
        if self.request.user.is_authenticated():
            comment_body=form.cleaned_data['comment']
            account=Account.objects.get(user=self.request.user)
            comment=Comment.objects.create(body=comment_body,account=account,article=article)
            comment.save()
            msg='评论成功'
            url = article.get_absolute_url()
        else:
            msg='登录之后才能发言哦'
            url=reverse('Main:login')
        data = {'message': msg, 'url': url}
        return render(self.request, 'message.html', data)
