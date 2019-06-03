from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator

from .models import Board, Post, Topic
from .forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# ___________________ Functions Based Views____________________________

def home(request):
	boards = Board.objects.all()
	context = {'boards': boards}
	return render(request, 'home.html', context)

def board_topics(request, pk):
	board = get_object_or_404(Board, pk=pk)
	queryset =  board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)

	page = request.GET.get('page',1)
	paginator =  Paginator(queryset, 20)

	try:
		topics = paginator.page(page)
	except PageNotAnInteger:
		topics = paginator.page(1)
	except EmptyPage:
		topics = paginator.page(paginator.num_pages)

	context = {'board': board, 'topics': topics}
	return render(request, 'topics.html', context)
#
# def new_topic(request, pk):
# 	board = get_object_or_404(Board, pk=pk)
# 	context = {'board': board}
# 	return render(request, 'new_topic_old.html', context)

@login_required
def new_topic(request, pk):
	board = get_object_or_404(Board, pk=pk)
	# user = User.objects.first()

	if request.method == 'POST':
		form = NewTopicForm(request.POST)
		if form.is_valid():
			# subject = request.POST['subject']
			# message = request.POST['message']
			# user = User.objects.first()  # TODO: get the currently logged in user
			# topic = Topic.objects.create(
			# 	subject=subject,
			# 	board=board,
			# 	starter=user
			# )

			topic = form.save(commit=False)
			topic.board = board
			topic.starter = request.user
			topic.save()

			post = Post.objects.create(
				message=form.cleaned_data.get('message'),
				topic=topic,
				created_by = request.user
			)
			return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
			# return redirect('board_topics', pk=board.pk)
	else:
		form = NewTopicForm()
	return render(request, 'new_topic.html', {'board': board, 'form':form})


def topic_posts(request, pk, topic_pk):
	topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
	topic.views += 1
	topic.save()
	return render(request, 'topic_posts.html', {'topic': topic})


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'



# ___________________ Class Based Views____________________________


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
	model = Post
	fields = ('message',)
	template_name = 'edit_post.html'
	pk_url_kwarg = 'post_pk'
	context_object_name = 'post'

	def form_valid(self, form):
		post = form.save(commit=False)
		post.updated_by = self.request.user
		post.updated_at = timezone.now()
		post.save()
		return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)