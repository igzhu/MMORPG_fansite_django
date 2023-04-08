from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
import random
from datetime import datetime
from .models import Message, Post, OneTimeCode
from .forms import MessageForm

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class MessageList(ListView):
    model = Message
    template_name = 'messages.html'
    context_object_name = 'messages'
    queryset = Message.objects.order_by('-messsageDateTime')
    paginate_by = 11

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msgs_total'] = Message.count_publications()
        context['membs_total'] = Member.count_members()
        context['psts_total'] = Post.count_posts()
        return context


class MessageDetails(DetailView):
    template_name = 'message_detail.html'
    queryset = Message.objects.all()


class MessageAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    # permission_required = ('board.add_message',)
    template_name = 'message_add.html'
    form_class = MessageForm

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = MessageForm()
    #     return context



class MessageEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    # permission_required = ('board.change_message',)
    template_name = 'message_add.html'
    form_class = MessageForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Message.objects.get(pk=id)


class MessageDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    # permission_required = ('board.delete_message',)
    template_name = 'message_delete.html'
    queryset = Message.objects.all()
    success_url = ''


class PostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    # queryset = Post.objects.filter(author=request.user).order_by('-postDateTime')
    paginate_by = 11

    def get_queryset(self, request):
        user = self.request.user
        queryset = super().get_queryset().filter(author=user).order_by('-postDateTime')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msgs_total'] = Message.count_publications()
        context['membs_total'] = Member.count_members()
        context['psts_total'] = Post.count_posts()
        return context


class PostDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ('board.delete_post',)
    template_name = 'board/message_delete.html'
    queryset = Message.objects.all()
    success_url = 'messages/'



@login_required
def respond_to_message(request, pk):
    msg = Message.objects.get(id=pk)
    messageAuthor = msg.user
    postAuthor = request.user
    postToMessage = msg
    postText = request.POST['response']

    resp = Post(messageAuthor=messageAuthor, postAuthor=postAuthor, postToMessage=postToMessage, postText=postText)
    resp.save()

    email = msg.author.email
    html = render_to_string(
          'board/email/response_submitted.html',
          {'msg': msg.messageTitle,
           "by_user": messageAuthor.username}
          )
    msg = EmailMultiAlternatives(
        subject=f'response to {msg.messageTitle}',
        body=f'You have a response to {msg.messageTitle}',
        from_email=DEFAULT_FROM_EMAIL,
        to=[email, ]
    )

    msg.attach_alternative(html, 'text/html')
    try:
        msg.send()
    except Exception as e:
        print(e)
        return redirect('')
    return redirect(request.META.get('HTTP_REFERER'))

def usual_login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        OneTimeCode.objects.create(code=''.join(random.sample('abcde', 2)), user=user)

        # email it
        # redirect to
    else:
        return redirect('invalid logon/')

def login_with_code_view(request):
    username = request.POST['username']
    code = request.POST['code']
    if OneTimeCode.objects.filter(code=code, user__username=username).exists():
        code = OneTimeCode.objects.get(code=code, user__username=username)
        if (datetime.now() - code.codeDateTime).total_seconts() // 60 > 2:
            code.delete()
            return redirect('code_expired/')
        login(request, request.user)
    else:
        return redirect('code_expired/')



"""from django.shortcuts import render
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages #import messages

from django.conf import settings
from django.urls import resolve
from django.shortcuts import redirect

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime

from django.core.cache import cache  # импорт для кэша

from .models import Post, Category, User, Author
from .filters import PostFilter
from .forms import PostForm

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class PostsList(ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    form_class = PostForm
    queryset = Post.objects.order_by('-postDatetime')
    paginate_by = 10

    def limit_posts(self):
        user = self.request.user
        #if Author.objects.get_or_create(authorName=user)[0]:
        if user.id:
            current_author = Author.objects.get_or_create(authorName=user)[0]
            time_now = datetime.now().date()
            posts_in_current_date = Post.objects.filter(postAuthor=current_author, postDatetime__date=time_now).count()
            if posts_in_current_date >= 3:
                messages.error(self.request, "Превышен лимит 3 поста в сутки !")
                return True
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        post_limited = self.limit_posts()
        context['post_limited'] = post_limited
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class PostDetails(DetailView):
    template_name = 'news/post_detail.html'
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        return context

    def get_object(self, *args, **kwargs):
        news_post = cache.get(f'news_article-{self.kwargs["pk"]}', None)  # 'None' returns when 'pk' not in the cache
        if not news_post:
            news_post = super().get_object(queryset=self.queryset)
            cache.set(f'news_article-{self.kwargs["pk"]}', news_post)
        return news_post


class PostSearch(ListView):
    model = Post
    template_name = 'post_search.html'
    context_object_name = 'posts'
    # form_class = PostForm
    # form_class = PostFilter
    queryset = Post.objects.order_by('-postDatetime')
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['authors'] = User.objects.all()
        # context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostAdd(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post',)
    template_name = 'news/post_add.html'
    # context_object_name = 'posts'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['categories'] = Category.objects.all()
        context['form'] = PostForm()
        return context

    def post(self, *args, **kwargs):
        form = self.form_class(self.request.POST)

        if form.is_valid():
            user = self.request.user
            post = form.save(commit=False)
            current_author = Author.objects.get_or_create(authorName=user)[0]
            post.postAuthor = current_author
            form.save()
            #return self.form.valid(form)
        '''  # этот кусок кода -альтернатива email by signal - рабочий !!!:
        user = self.request.user
        #post = form.save(commit=False)
        
        time_now = datetime.now().date()
        posts_in_current_date = Post.objects.filter(postAuthor=current_author, postDatetime__date=time_now).count()
        if posts_in_current_date >= 3:
            messages.error(request, "Превышен лимит 3 поста в сутки !")
            return redirect('/posts/')

        if form.is_valid():
            #form.fields['postAuthor'] = current_author
            post = form.save(commit=False)
            post.postAuthor = current_author
            form.save()
            header = form.cleaned_data.get("head")
            txt = form.cleaned_data.get('postText')  # .[:51]
            ctgries = form.cleaned_data.get("category")
            for ctgr in ctgries:
                categ = Category.objects.get(name=ctgr.name)
                cat_users = categ.subscribers.all()
                for usr in cat_users:
                    html_content = render_to_string('news/mail_in_category.html',
                       {'headr': header,
                        'catgor': categ.name,
                        'text': txt,
                        'nam': usr.username,
                        'e_mail': usr.email, }
                    )
                    msg = EmailMultiAlternatives(
                        subject=header,
                        body=txt[:51],
                        from_email=DEFAULT_FROM_EMAIL,
                        to=[usr.email, ]
                    )
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()
        '''  # этот кусок кода - альтернатива email by signal - рабочий !!!


        return redirect('/posts/')



class PostEdit(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post',)
    template_name = 'news/post_add.html'
    form_class = PostForm

    # login_url = '/login/'
    # redirect_field_name = 'redirect_to'
    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

    # def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
    #    return context


class PostDelete(LoginRequiredMixin, DeleteView):
    template_name = 'news/post_delete.html'
    queryset = Post.objects.all()
    success_url = '/posts/'

    # def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)
    #    context['is_not_premium'] = not self.request.user.groups.filter(name='authors').exists()
    #    return context


@login_required
def upgrade_me_to_author(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        premium_group.user_set.add(user)
    return redirect('/posts/')


@login_required
def subscribe_to_category(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    if not category.subscribers.filter(id=user.id).exists():
        category.subscribers.add(user)
        email = user.email
        html = render_to_string(
            'news/mail_subscribe.html',
            {'categry': category,
             "user": user}
        )
        msg = EmailMultiAlternatives(
            subject=f'{category} subscription',
            body='You are subscribed.',
            from_email=DEFAULT_FROM_EMAIL,
            to=[email, ]
        )

        msg.attach_alternative(html, 'text/html')
        try:
            msg.send()
        except Exception as e:
            print(e)
            return redirect('/posts/')
    return redirect(request.META.get('HTTP_REFERER'))


@login_required
def unsubscribe_from_category(request, pk):
    user = request.user
    c = Category.objects.get(id=pk)
    if c.subscribers.filtet(id=user.id).exists():
        c.subscribers.remove(user)
    return redirect('/posts/'
                    )


class PostCategoryView(ListView):
    model = Post
    template_name = 'news/category.html'
    context_object_name = 'posts'
    # ordering = ['-postDatetime']
    queryset = Post.objects.order_by('-postDatetime')
    paginate_by = 10

    def get_queryset(self):
        self.id = resolve(self.request.path_info).kwargs['pk']
        ctgr = Category.objects.get(id=self.id)
        queryset = Post.objects.filter(category=ctgr).order_by('-postDatetime')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        categry = Category.objects.get(id=self.id)
        subscribed = categry.subscribers.filter(email=user.email)
        if not subscribed:
            context['ctgry'] = categry
        return context
"""
