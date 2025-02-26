from django.http import HttpResponse
from django.template import loader

# Create your views here.
def index(request):
    template = loader.get_template("aniTA_app/index.html")
    context = {}
    return HttpResponse(template.render(context, request))

def dashboard(request, arg_foo):
    template = loader.get_template("aniTA_app/dashboard.html")
    context = { "arg_foo": arg_foo }
    return HttpResponse(template.render(context, request))


