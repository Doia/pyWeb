import random
import numpy as np
from myapp import nnSnake as nn
from concurrent.futures import ThreadPoolExecutor

class AlgoritmoEvolutivo():

    def __init__(self, population_size=21):
        self.population_size = population_size
        self.population = []
        self.generation = 0
        for i in range(population_size):
            self.population.append(nn.RedNeuronal(i+1))

    def select_parents(self):
        prob_select = [rn.fitness for rn in self.population]
        # print(prob_select)
        parents = np.random.choice(self.population, size=2, p=prob_select/np.sum(prob_select))
        return parents[0], parents[1]
    
    def select_parents_by_tournament(self, tournament_size=3):
        def tournament_selection():
            # Seleccionar `tournament_size` individuos al azar
            selected = np.random.choice(self.population, size=tournament_size)
            # Devolver el individuo con la mayor aptitud de entre los seleccionados
            return max(selected, key=lambda rn: rn.fitness)

        # Seleccionar dos padres usando torneo
        parent1 = tournament_selection()
        parent2 = tournament_selection()

        return parent1, parent2

    # def crossover(self, parent1, parent2):
    #     child = nn.RedNeuronal(0)
    #     for i in range(len(child.model.layers)):
    #         if random.random() < 0.5:
    #             child.model.layers[i].set_weights(parent1.model.layers[i].get_weights())
    #         else:
    #             child.model.layers[i].set_weights(parent2.model.layers[i].get_weights())
    #     return child
    
    # def crossoverPesos(self, parent1, parent2):
    #     child = nn.RedNeuronal(0)
    #     for i in range(len(child.model.layers)):
    #         # Tomamos los pesos de los padres
    #         weights1 = parent1.model.layers[i].get_weights()
    #         weights2 = parent2.model.layers[i].get_weights()
            
    #         # Establecemos una lista vacía para los nuevos pesos
    #         new_weights = []
            
    #         # Iteramos sobre los pesos (podría incluir pesos y biases)
    #         for w1, w2 in zip(weights1, weights2):
    #             # Verificamos si es un array de pesos o un bias
    #             if len(w1.shape) == 2:  # Es una matriz de pesos
    #                 # Creamos una máscara de cruce binaria
    #                 mask = np.random.randint(2, size=w1.shape)
    #                 new_weight = np.where(mask, w1, w2)
    #             else:  # Es un bias
    #                 mask = np.random.randint(2, size=w1.shape)
    #                 new_weight = np.where(mask, w1, w2)
    #             new_weights.append(new_weight)
                
    #         # Establecemos los nuevos pesos en el hijo
    #         child.model.layers[i].set_weights(new_weights)
        
    #     return child

    def one_point_layer_crossover(self, parent1_weights, parent2_weights):
        # Escoge un punto de cruce aleatorio
        crossover_point = random.randint(0, len(parent1_weights[0]))

        # Divide y combina los pesos según el punto de cruce
        child1_weights = [np.concatenate([parent1_weights[0][:crossover_point], parent2_weights[0][crossover_point:]]), parent1_weights[1]]
        child2_weights = [np.concatenate([parent2_weights[0][:crossover_point], parent1_weights[0][crossover_point:]]), parent2_weights[1]]

        return child1_weights, child2_weights

    def crossover(self, parent1, parent2):
        child = nn.RedNeuronal(0)
        for i in range(len(child.model.layers)):
            if random.random() < 0.5:
                child.model.layers[i].set_weights(parent1.model.layers[i].get_weights())
            else:
                parent1_weights = parent1.model.layers[i].get_weights()
                parent2_weights = parent2.model.layers[i].get_weights()
                
                # Asegurarse de que la capa tiene pesos para cruzar (es decir, no es una capa Flatten)
                if parent1_weights:
                    child1_weights, child2_weights = self.one_point_layer_crossover(parent1_weights, parent2_weights)

                    # Decidir aleatoriamente qué conjunto de pesos (de los dos hijos) asignar a la capa del hijo
                    if random.random() < 0.5:
                        child.model.layers[i].set_weights(child1_weights)
                    else:
                        child.model.layers[i].set_weights(child2_weights)

        return child

    def mutate(self, child):
        for layer in child.model.layers:
            if random.random() < 0.2:  # Probabilidad de mutación por capa
                weights = layer.get_weights()
                weights = [w + (np.random.random(w.shape) - 0.5)*0.1 for w in weights]
                layer.set_weights(weights)

    def get_elite(self, num_elite=2):
        # Devuelve los num_elite individuos más aptos
        return sorted(self.population, key=lambda x: x.fitness, reverse=True)[:num_elite]
   
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


        # Añadir individuos élite
        elite_individuals = self.get_elite(2)
        new_population.extend(elite_individuals)
        
        # Generar nueva población manteniendo los individuos élite
        for _ in range(self.population_size - len(elite_individuals)):
            parent1, parent2 = self.select_parents_by_tournament()
            if random.random() < 0.8:  # Probabilidad de mutación por capa
                child = self.crossover(parent1, parent2)
                self.mutate(child)
                new_population.append(child)
            else:
                new_population.append(nn.RedNeuronal(0))
                self.mutate(parent1)
            
        
        self.population = new_population

        #ids que existen
        actualIDs = []
        for i in range(self.population_size):
            if (self.population[i].id not in actualIDs):
                actualIDs.append(self.population[i].id)
            else:
                self.population[i].id = 0

        # print(actualIDs)

        for i in range(self.population_size):
            if (self.population[i].id == 0):
                for j in range(1,22):
                    if (j not in actualIDs):
                        self.population[i].id = j
                        actualIDs.append(j)
                        break

        for i in range(self.population_size):
            print(self.population[i].id)
            

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
# ae = AlgoritmoEvolutivo()
# ae.evolve(data, labels, 50)

