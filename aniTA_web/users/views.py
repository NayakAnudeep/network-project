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
            # Improved error handling for JSON parsing
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                # Handle form data if not JSON
                data = {
                    'name': request.POST.get('name', ''),
                    'email': request.POST.get('email', ''),
                    'password': request.POST.get('password', ''),
                    'role': request.POST.get('role', 'student')
                }
            
            # Validate required fields
            if not all([data.get('name'), data.get('email'), data.get('password')]):
                return JsonResponse({"error": "Missing required fields"}, status=400)
                
            # Try to register the user with ArangoDB
            try:
                response = register_user(data['name'], data['email'], data['password'], data.get('role', 'student'))
                
                # Set success message in session
                if 'flash_success' not in request.session:
                    request.session['flash_success'] = []
                request.session['flash_success'].append("Account created! Please log in.")
                
                return JsonResponse(response)
            except Exception as e:
                print(f"ArangoDB Registration error: {str(e)}", flush=True)
                return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
                
        except Exception as e:
            print(f"Registration error: {str(e)}", flush=True)
            return JsonResponse({"error": str(e)}, status=400)
            
    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            # Try to parse JSON data from request body
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                # Handle form data if not JSON
                data = {
                    'email': request.POST.get('email', ''),
                    'password': request.POST.get('password', '')
                }
            
            # Validate required fields
            if not all([data.get('email'), data.get('password')]):
                return JsonResponse({"error": "Missing email or password"}, status=400)
                
            match authenticate_user(data['email'], data['password']):
                case {"failure": None, "user_id": user_id, "username": username, "role": role }:
                    request.session['user_id'] = user_id
                    request.session['username'] = username
                    request.session['role'] = role
                    request.session.save()
                    
                    # Check if there's a 'next' parameter for redirection
                    next_url = request.GET.get('next', '/')
                    return JsonResponse({"success": True, "redirect": next_url})
                case x:
                    response = x
            return JsonResponse(response)
        except Exception as e:
            return JsonResponse({"error" : str(e)}, status = 400)
    
    # For GET requests, render the login page
    return render(request, 'users/login.html', {
        'next': request.GET.get('next', '/')
    })

@csrf_exempt
def logout(request):
    if request.method == "POST":
        request.session.flush()
        if 'flash_success' not in request.session:
            request.session['flash_success'] = []
        request.session['flash_success'].append("Logged out successfully.")
        return redirect('/')
    return JsonResponse({"error": "Invalid request"}, status=400)
