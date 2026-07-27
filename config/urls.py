from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include("core.urls")),
    #path('api/',include("core.urls")),

    #path("login/", views.login, name="login"),
    #path("register/", views.register, name="register"),
    #path("dashboard/", views.dashboard, name="dashboard"),
    #path("clients/", views.clients, name="clients"),
    #path("campaigns/", views.campaigns, name="campaigns"), 
    #path("ai_chat/",views.ai_chat,name="ai_chat"),
    #path("meetings/",views.meetings,name="meetings"),
    #path("audit/",views.audit,name="audit"),
    #path("templates/",views.templates,name="templates"),

]

# from django.contrib import admin
# from django.urls import path,include
# from . import views

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('',include('core.urls')),

# ]



