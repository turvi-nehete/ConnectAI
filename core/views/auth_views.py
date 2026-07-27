from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json

from django.http import JsonResponse

from core.models import Profile


def register_view(request):

    if request.method == "POST":
        print("REGISTER VIEW")
        data = json.loads(request.body)

        name = data["name"]
        email = data["email"]
        password = data["password"]

        print(email)
        print(password)

        if User.objects.filter(username=email).exists():

            return JsonResponse({
                "message":"User already exists"
            }, status=400)

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        return JsonResponse({
            "message":"User Registered Successfully"
        })

    return render(request, "register.html")


def login_view(request):

    if request.method == "POST":
        print("Login View Fired")
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(email)
        print(password)

        try:
            user_obj = User.objects.get(email=email)
            print("Username:", user_obj.username)

            user = authenticate(
                request,
                username=user_obj.username,
                password=password
            )

            print("Authenticated User:", user)

        except User.DoesNotExist:
            print("User not found")
            user = None

        if user is not None:
            print("LOGIN SUCCESS")
            login(request, user)
            return redirect("dashboard")

        print("LOGIN FAILED")
        messages.error(request, "Invalid email or password.")

    return render(request, "login.html")


def logout_view(request):

    logout(request)

    return redirect("login")