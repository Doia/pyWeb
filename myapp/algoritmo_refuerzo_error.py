import random
import numpy as np
from myapp import nnSnake as nn
from concurrent.futures import ThreadPoolExecutor

class AlgoritmoRefuerzoError():

    def __init__(self, population_size=21):
        self.population_size = population_size
        self.population = []
        self.generation = 0
        for i in range(population_size):
            self.population.append(nn.RedNeuronal(i+1))

    def evolve(self, data):
        self.generation += 1
        new_population = []
        
        # Evaluar población
        for gameRes in data['allGames']:
            for rn in self.population:
                if (gameRes['id'] == rn.id):
                    rn.setFitness(gameRes['fitness'])
                    break

        best_fitness = max([rn.fitness for rn in self.population])

        for gameRes in data['allGames']:
             for rn in self.population:
                if (gameRes['id'] == rn.id):

                    board = gameRes['final_state']['board']
                    for i in range(len(board)):
                        for j in range(len(board[i])):
                            north = None
                            east = None
                            west = None
                            south = None
                            if board[i][j] == 1:
                                if i > 0:
                                    north = board[i-1][j]
                                if i < len(board) - 1:
                                    south = board[i+1][j]
                                if j > 0:
                                    west = board[i][j-1]
                                if j > len(board[i]) - 1:
                                    east = board[i-1][j+1]
                    
                    good_direction = None
                    if north == 3:
                        good_direction = 'UP'
                    elif east == 3:
                        good_direction = 'RIGTH'
                    elif south == 3:
                        good_direction = 'DOWN'
                    elif west == 3:
                        good_direction = 'LEFT'
                    
    
                    elif north == 0:
                        good_direction = 'UP'
                    elif east == 0:
                        good_direction = 'RIGTH'
                    elif south == 0:
                        good_direction = 'DOWN'
                    elif west == 0:
                        good_direction = 'LEFT'
                    
                    state = { 'board': gameRes['final_state']['board'], 'bad_direction': gameRes['final_state']['direction'], 'good_direction': good_direction }

                    if gameRes['id'] == 1:
                        rn.train_nn(state, True)
                    else:
                        rn.train_nn(state, False)
                
            
        # Mostrar el fitness del mejor individuo
        print(f"Generación {self.generation+1} - Mejor Fitness: {best_fitness:.4f}")

    def nextMoves(self, data):

        proccessData = []
        #añadimos al estado del juego la rn que tiene ese id
        for state in data['allGames']:
    
            proccessData.append({
                'id': state['id'],
                'gameState': { 'board': state['board'], 'direction': state['direction'] },
            })

        # Define una función para usarla con el ThreadPool
        def task(state):
            redN = None
            for rn in self.population:
                if (rn.id == state['id']):
                    redN = rn
                    break

            if redN is None:
                # Aquí puedes manejar el caso en que no se encuentre una red neuronal
                # Por ejemplo, puedes retornar un valor predeterminado o generar un error específico
                return {
                    "id": state['id'], 
                    "error": "No se encontró una red neuronal con el id correspondiente"
                }

            return {
                "id": state['id'], 
                "next_move": redN.predict_next_move(state['gameState'])
            }
        
        # Paraleliza la ejecución con ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            games = list(executor.map(task, proccessData))

        return games
    
    def __str__(self):
        return f"Algoritmo Evolutivo con una población de {self.population_size} redes neuronales."

# Ejemplo de uso:
# ae = AlgoritmoRefuerzoError()

