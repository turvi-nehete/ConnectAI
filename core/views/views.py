from django.shortcuts import render
def login(request):
    return render(request,"login.html")

def register(request):
    return render(request, "register.html")

# def dashboard(request):
#     return render(request, "dashboard.html")

def clients(request):
    return render(request, "clients.html")

# def campaigns(request):
#     return render(request, "campaigns.html")

def ai_chat(request):
    return render(request,"ai_chat.html")

def meetings(request):
    return render(request,"meetings.html")

# def audit(request):
#     return render(request,"audit.html")

# def templates(request):
#     return render(request,"templates.html")



