from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from random import randrange
from todolist.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
# Create your views here.


def usignup(request):
    if request.method == "POST":
        un = request.POST.get("UserName")
        em = request.POST.get("Email")
        try:
            usr = User.objects.get(username=un)
            return render(request, 'usignup.html', {'msg': 'Username not available '})
        except User.DoesNotExist:
            try:
                usr = User.objects.get(email=em)
                return render(request, 'usignup.html', {'msg': 'You have an account'})
            except User.DoesNotExist:
                text = '1234567890abcdefghijklmnopqrstuvwxyz!@#$%^&*+-'
                pw = ""
                for i in range(6):
                    pw = pw+text[randrange(len(text))]
                send_mail('ToDo password', "Your password is  " + pw, EMAIL_HOST_USER, [em])
                usr = User.objects.create_user(
                    username=un, password=pw, email=em)
                print(pw)
                usr.save()
                return redirect('ulogin')

    else:
        return render(request, 'usignup.html')


def ulogin(request):
    if request.method == "POST":
        un = request.POST.get("UserName")
        pw = request.POST.get("Password")
        usr = authenticate(username=un, password=pw)
        if usr is None:
            return render(request, 'ulogin.html', {'msg': 'Invalid credential'})
        else:
            login(request, usr)
            return redirect("home")
    else:
        return render(request, "ulogin.html")


def rpassword(request):
    if request.method == "POST":
        un = request.POST.get("UserName")
        em = request.POST.get("Password")
        try:
            usr = User.objects.get(username=un) and User.objects.get(email=em)
            text = '1234567890abcdefghijklmnopqrstuvwxyz!@#$%^&*+-'
            pw = ""
            for i in range(7):
                pw = pw+text[randrange(len(text))]
            send_mail('ToDo ResetPassword', "Your password is" +
                      pw, EMAIL_HOST_USER, [em])
            usr = User.objects.create_user(username=un, password=pw, email=em)
            usr.save()
            return redirect('ulogin')
        except User.DoesNotExist:
            return render(request, 'rpassword.html', {'msg': 'Invalid Credentials'})
    else:
        return render(request, "rpassword.html")


def ulogout(request):
    logout(request)
    return redirect('ulogin')
