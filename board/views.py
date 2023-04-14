from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail.message import EmailMultiAlternatives
import random
from datetime import datetime
from .models import Message, Post, OneTimeCode
from .filters import PostFilter
from .forms import MessageForm

DEFAULT_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


class MessageList(ListView):
    model = Message
    template_name = 'messages.html'
    context_object_name = 'messages'
    queryset = Message.objects.order_by('-messageDateTime')
    paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msgs_total'] = Message.objects.all().count()
        context['membs_total'] = User.objects.all().count() - 1
        context['psts_total'] = Post.objects.all().count()
        return context


class MessageDetails(DetailView):
    template_name = 'message_details.html'
    queryset = Message.objects.all()


class MessageAdd(LoginRequiredMixin, CreateView):
    model = Message
    # permission_required = ('board.add_message',)
    template_name = 'message_add.html'
    form_class = MessageForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm(self.request.POST or None, self.request.FILES or None)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(self.request.POST or None, self.request.FILES or None)

        if form.is_valid():
            user = self.request.user
            message = form.save(commit=False)
            message.author = user
            form.save()
        return redirect('/')


class MessageEdit(LoginRequiredMixin, UpdateView):
    # permission_required = ('board.change_message',)
    template_name = 'message_add.html'
    form_class = MessageForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Message.objects.get(pk=id)


class MessageDelete(LoginRequiredMixin, DeleteView):
    # permission_required = ('board.delete_message',)
    template_name = 'message_delete.html'
    queryset = Message.objects.all()
    success_url = '/'


class PostList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset().filter(postToMessage__author=user).order_by('-postDateTime')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['msgs_total'] = Message.objects.all().count()
        context['membs_total'] = User.objects.all().count() - 1
        context['psts_total'] = Post.objects.all().count()
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostDetails(DetailView):
    template_name = 'post_details.html'
    queryset = Post.objects.all()


class PostDelete(LoginRequiredMixin, DeleteView):
    permission_required = ('board.delete_post',)
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/posts'
    # return redirect(request.META.get('HTTP_REFERER'))


@login_required
def respond_to_message(request, pk):
    msg = Message.objects.get(id=pk)
    postAuthor = request.user
    postToMessage = msg
    postText = request.POST.get('response', 'nope')

    resp = Post(postAuthor=postAuthor, postToMessage=postToMessage, postText=postText)
    resp.save()
    return redirect('/')
    """  отправка email перенесенa в signals.py
    email = msg.author.email
    html = render_to_string(
          'board/email/response_submitted.html',
          {'msg': msg.messageTitle,
           "by_user": msg.author.username}
          )
    msg = EmailMultiAlternatives(
        subject=f'response to message "{msg.messageTitle}"',
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
    return redirect('/posts')
    # return redirect(request.META.get('HTTP_REFERER'))
    """


@login_required
def approve_post(request, pk):
    pos = Post.objects.get(id=pk)
    # pos.accept()
    pos.postAccepted = True
    pos.save()
    return redirect('/posts')
    """  отправка email перенесенa в signals.py
    pos_author = pos.postAuthor
    pos_text = pos.postText[:20]

    email = pos_author.email
    approve_html = render_to_string(
          'board/email/accept_post.html',
          {'post': pos_text,
           "to_msg": pos.postToMessage}
          )
    msg = EmailMultiAlternatives(
        subject=f'"{pos_texte}" accepted',
        body=f'{pos_texte} accepted',
        from_email=DEFAULT_FROM_EMAIL,
        to=[email, ]
    )

    msg.attach_alternative(html, 'text/html')
    try:
        msg.send()
    except Exception as e:
        print(e)
    return redirect('/posts')
    # return redirect(request.META.get('HTTP_REFERER'))
"""

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

