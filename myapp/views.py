
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from .models import Persona
from myapp import nnSnake as nn
from myapp import algoritmo_evolutivo as algEv
from django.views.decorators.csrf import csrf_exempt
import json

import time

def home(request):
    persona = Persona.objects.first()  # Obtiene la primera persona
    return render(request, 'home.html', {'person': persona})
    
def snake_game(request):
    global algoritmoEvolutivo
    algoritmoEvolutivo = algEv.AlgoritmoEvolutivo(21)
    return render(request, 'snake_game.html')

@csrf_exempt
def next_snake_move(request):
    if request.method == "POST":
        data = json.loads(request.body)
        games = algoritmoEvolutivo.nextMoves(data)

        return JsonResponse({'games': games})
    
@csrf_exempt
def next_snake_gen(request):
    if request.method == "POST":
        data = json.loads(request.body)
        algoritmoEvolutivo.evolve(data)

        return JsonResponse({'ok': 'ok'})

