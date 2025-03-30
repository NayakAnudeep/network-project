from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect

# Create your views here.
def index(request):
    if request.session.get('user_id'):
        return redirect('/dashboard')
    else:
        template = loader.get_template("aniTA_app/index.html")
        context = dict()
        context['flash_success'] = request.session.pop('flash_success', [])
        return HttpResponse(template.render(context, request))

def dashboard(request):
    template = loader.get_template("aniTA_app/dashboard.html")
    context = {}
    return HttpResponse(template.render(context, request))

def courses(request):
    template = loader.get_template("aniTA_app/courses.html")
    context = {}
    return HttpResponse(template.render(context, request))
