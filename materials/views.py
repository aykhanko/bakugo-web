from django.shortcuts import render
from .models import ProjectMaterial


def materials_index(request):
    material = ProjectMaterial.objects.filter(is_active=True).first()
    return render(request, 'materials/index.html', {'material': material})

