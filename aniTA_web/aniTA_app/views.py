from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect

# Create your views here.
def index(request):
    template = loader.get_template("aniTA_app/index.html")
    # NOTE: This should be the template if the user is NOT logged in.
    # We should have an alternate html template for a logged in user.
    context = {}
    return HttpResponse(template.render(context, request))

def login(request):
    if request.method == "POST":
        # TODO authentication
        # Can redirect back to home ('/') but display a different view when logged in.
        return redirect('/')
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405);

def signup(request):
    if request.method == "POST":
        # TODO add account to D.B.
        return redirect('/')
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405);    

def dashboard(request):
    template = loader.get_template("aniTA_app/dashboard.html")
    context = {}
    return HttpResponse(template.render(context, request))

def courses(request):
    template = loader.get_template("aniTA_app/courses.html")
    context = {}
    return HttpResponse(template.render(context, request))


