from django import template
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage

register=template.Library()

@register.simple_tag(takes_context=True)
def paginate(context,obj_list,page_count):
    left=3
    right=3
    paginator=Paginator(obj_list,page_count)
    page=context['request'].GET.get('page')

    try:
        obj_list=paginator.page(page)
        context['current_page']=int(page)
        pages=get_left(context['current_page'],left,paginator.num_pages)+\
              get_right(context['current_page'],right,paginator.num_pages)
    except PageNotAnInteger:
        obj_list=paginator.page(1)
        context['current_page']=1
        pages=get_right(context['current_page'],right,paginator.num_pages)

    context['obj_list']=obj_list
    context['pages']=pages
    context['first_page']=1
    context['last_page']=paginator.num_pages

    try:
        context['pages_first']=pages[0]
        context['pages_last']=pages[-1]+1
    except IndexError:
        context['pages_first']=1
        context['pages_last']=2

    return ''

def get_left(current_page,left,num_pages):
    if current_page==1:
        return []
    if current_page==num_pages:
        l=[i-1 for i in range(current_page,current_page-left,-1) if i-1>1]
        l.sort()
        return l
    l=[i for i in range(current_page,current_page-left,-1) if i>1]
    l.sort()
    return l

def get_right(current_page,right,num_pages):
    if current_page==num_pages:
        return []
    return [i+1 for i in range(current_page,current_page+right-1) if i+1<num_pages]
