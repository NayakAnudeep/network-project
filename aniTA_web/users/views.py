from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from .arangodb import register_user
from .arangodb import authenticate_user

@csrf_exempt
def register(request):
    if request.method == "POST":
        try: 
            data = json.loads(request.body)
            response = register_user(data['username'], data['email'], data['password'], data.get('role', 'student'))
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status = 400)
    return JsonResponse({"error" : "Invalid request"}, status = 400)

@csrf_exempt
def login(request):
    if request.method == "POST": 
        try: 
            data = json.loads(request.body)
            response = authenticate_user(data['email'], data['password'])
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status = 400)
    return JsonResponse({"error" : "Invalid request"}, status = 400)
