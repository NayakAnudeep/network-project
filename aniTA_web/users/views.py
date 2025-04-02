from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import json
from django.http import JsonResponse
from .arangodb import register_user
from .arangodb import authenticate_user

@csrf_exempt
def register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            response = register_user(data['name'], data['email'], data['password'], data.get('role', 'student'))
            if 'flash_success' not in request.session:
                request.session['flash_success'] = []
            request.session['flash_success'].append("Account created! Please log in.")
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status = 400)
    return JsonResponse({"error" : "Invalid request"}, status = 400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            match authenticate_user(data['email'], data['password']):
                case {"failure": None, "user_id": user_id, "username": username, "role": role }:
                    request.session['user_id'] = user_id
                    request.session['username'] = username
                    request.session['role'] = role
                    request.session.save()
                    response = {"success": True}
                case x:
                    response = x
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status = 400)
    return JsonResponse({"error" : "Invalid request"}, status = 400)

@csrf_exempt
def logout(request):
    if request.method == "POST":
        request.session.flush()
        if 'flash_success' not in request.session:
            request.session['flash_success'] = []
        request.session['flash_success'].append("Logged out successfully.")
        return redirect('/')
    return JsonResponse({"error": "Invalid request"}, status=400)
