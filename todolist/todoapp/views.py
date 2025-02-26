from django.core.exceptions import MultipleObjectsReturned
from todoapp.models import Tasktodo
from django.shortcuts import render, redirect
# Create your views here.


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('ulogin')


def create(request):
    if request.method == "POST":
        t = request.POST.get("Task")
        ta = Tasktodo.objects.create(task=t, usname=request.user)
        ta.save()
        return render(request, 'home.html', {'msg': 'Task Added Sucessfully'}
                      )
    else:
        return render(request, 'home.html')


def deletetask(request, t, da):
    try:
        ds = Tasktodo.objects.get(task=t)
        ds.delete()
        return render(request, 'home.html')
    except MultipleObjectsReturned:
        datee = Tasktodo.objects.get(task_date=da)
        datee.delete()
        return render(request, 'home.html')


def viewtask(request):
    if request.user.is_authenticated:
        d = Tasktodo.objects.filter(usname=request.user)
        return render(request, 'home.html', {'data': d})
    else:
        return redirect('ulogin')
