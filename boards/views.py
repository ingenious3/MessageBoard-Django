from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Board, Post, Topic
from .forms import NewTopicForm

def home(request):
	boards = Board.objects.all()
	context = {'boards': boards}
	return render(request, 'home.html', context)

def board_topics(request, pk):
	board = get_object_or_404(Board, pk=pk)
	context = {'board': board}
	return render(request, 'topics.html', context)
#
# def new_topic(request, pk):
# 	board = get_object_or_404(Board, pk=pk)
# 	context = {'board': board}
# 	return render(request, 'new_topic_old.html', context)

def new_topic(request, pk):
	board = get_object_or_404(Board, pk=pk)
	user = User.objects.first()

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
			topic.starter = user
			topic.save()

			post = Post.objects.create(
				message=form.cleaned_data.get('message'),
				topic=topic,
				created_by=user
			)
			return redirect('board_topics', pk=board.pk)
	else:
		form = NewTopicForm()
	return render(request, 'new_topic.html', {'board': board, 'form':form})