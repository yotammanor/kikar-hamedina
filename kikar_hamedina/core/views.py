from django.shortcuts import render
from .models import Facebook_Status, Person


def index(request):
    statuses = Facebook_Status.objects.order_by('?')

    return render(request, 'core/index.html', {'statuses': statuses})
