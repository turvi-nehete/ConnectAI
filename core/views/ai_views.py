from django.shortcuts import render
from core.models import Client
from core.audit import log_activity

def chat(request):

    clients = Client.objects.filter(uid=request.user)

    states = sorted({
        state.strip().title()
        for state in clients.values_list("state", flat=True)
        if state
    })

    cities = sorted({
        city.strip().title()
        for city in clients.values_list("city", flat=True)
        if city
    })

    countries = sorted({
        country.strip().title()
        for country in clients.values_list("country", flat=True)
        if country
    })

    context = {
    "customer_types": Client.CUSTOMER_CHOICES,
    "company_types": Client.COMPANY_CHOICES,
    "states": states,
    "cities": cities,
    "countries": countries,
    "clients": clients.order_by("comp_name"),
}

    return render(
        request,
        "ai_chat.html",
        context
    )


import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.agents import generate_ai_email
from django.views.decorators.http import require_POST

@require_POST
def generate_email(request):
    data = json.loads(request.body)

    prompt = data.get("prompt")

    result = generate_ai_email(prompt)

    log_activity(
    request.user,
    "Generate Email",
    prompt,
    "LLM"
)

    return JsonResponse(result)

from core.agents import generate_ai_email
from core.agents import (
    generate_ai_email,
    generate_ai_email_rag,
)

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from core.audit import log_activity


@require_POST
def generate_email_rag(request):

    prompt = request.POST.get("prompt")
    uploaded_pdf = request.FILES.get("pdf")

    if not uploaded_pdf:
        return JsonResponse(
            {
                "error": "No PDF uploaded."
            },
            status=400
        )

    result = generate_ai_email_rag(
        prompt,
        uploaded_pdf
    )

    log_activity(
        request.user,
        "Generate Email (RAG)",
        prompt,
        "RAG + LLM"
    )

    return JsonResponse(result)