from django.shortcuts import render
from django.http import HttpResponse
from .models import Board

def home(request):
	boards = Board.objects.all()
	context = {'boards': boards}
	return render(request, 'home.html', context)