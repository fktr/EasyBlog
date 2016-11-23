from django.contrib import admin
from .models import Article,Tag,Category,Account,Comment

# Register your models here.
admin.site.register(Account)
admin.site.register(Comment)
admin.site.register(Article)
admin.site.register(Category)
admin.site.register(Tag)
