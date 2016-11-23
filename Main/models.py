from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import collections

# Create your models here.
class Category(models.Model):
    name=models.CharField('类名',max_length=16)
    created_time=models.DateTimeField('创建时间',auto_now_add=True)
    last_modified_time=models.DateTimeField('修改时间',auto_now=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name=models.CharField('标签名',max_length=16)
    created_time=models.DateTimeField('创建时间',auto_now_add=True)
    last_modified_time=models.DateTimeField('修改时间',auto_now=True)

    def __str__(self):
        return self.name

class ArticleManager(models.Manager):

    def archive(self):
        date_list=Article.objects.datetimes('created_time','month','DESC')
        date_dict=collections.defaultdict(list)
        for d in date_list:
            date_dict[d.year].append(d.month)
        return sorted(date_dict.items(),reverse=True)

class Article(models.Model):
    STATUS_CHOICE=(
        ('d','Draft'),
        ('p','Published'),
    )

    objects=ArticleManager()
    title=models.CharField('标题',max_length=32)
    abstract=models.CharField('摘要',max_length=64)
    body=models.TextField('正文')
    created_time=models.DateTimeField('创建时间',auto_now_add=True)
    last_modified_time=models.DateTimeField('修改时间',auto_now=True)
    status=models.CharField('状态',max_length=1,choices=STATUS_CHOICE,default='d')
    category=models.ForeignKey('Category',verbose_name='类名')
    tag=models.ManyToManyField('Tag',verbose_name='标签集合')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('Main:article',kwargs={'article_id':self.pk})

    class Meta:
        ordering=['-last_modified_time']

class Account(models.Model):
    user=models.OneToOneField(User,verbose_name='用户')
    created_time=models.DateTimeField('注册时间',auto_now_add=True)

    def __str__(self):
        return self.user.username

class Comment(models.Model):
    account=models.ForeignKey('Account',verbose_name='评论账户')
    body=models.CharField('评论内容',max_length=128)
    article=models.ForeignKey('Article',verbose_name='评论博客')
    created_time=models.DateTimeField('评论时间',auto_now_add=True)

    def __str__(self):
        return self.body

    class Meta:
        ordering=['-created_time']
