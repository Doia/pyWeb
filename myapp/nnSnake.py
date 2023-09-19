import numpy as np
import tensorflow as tf
from tensorflow import keras

# Dimensiones del tablero (por ejemplo, 10x10)
BOARD_SIZE = 10

# Mapeo de direcciones a números
DIRECTION_MAP = {
    'UP': 0,
    'RIGHT': 1,
    'DOWN': 2,
    'LEFT': 3
}

class RedNeuronal():

    def __init__(self):
        self.id = None
        self.model = self.build_model()
        self.fitness = 0.0

    def __init__(self, id):
        self.id = id
        self.model = self.build_model()
        self.fitness = 0.0

    def setFitness(self, fitness):
        self.fitness = fitness

    def setId(self, id):
        self.id = id

    def build_model(self):
        return self.build_snake_deep_nn()
    
    def build_model_simple(self):
        # La entrada ahora incluirá el tablero y una dimensión adicional para la dirección
        input_shape = (BOARD_SIZE, BOARD_SIZE + 1, 1) 

        model = keras.Sequential([
            keras.layers.Flatten(input_shape=input_shape),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(4)  # 4 direcciones posibles: UP, DOWN, LEFT, RIGHT
        ])

        model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])
        return model
    
    def build_feedforward_deep(self):
        model = keras.Sequential([
            keras.layers.Flatten(input_shape=(BOARD_SIZE, BOARD_SIZE + 1, 1)),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(4)
        ])
        model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])
        return model
    
    def build_convolutional(self):
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(BOARD_SIZE, BOARD_SIZE + 1, 1)),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(4)
        ])
        model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])
        return model
    
    def build_regularized(self):
        model = keras.Sequential([
            keras.layers.Flatten(input_shape=(BOARD_SIZE, BOARD_SIZE + 1, 1)),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(256, activation='relu'),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(4)
        ])
        model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])
        return model

    def build_snake_deep_nn(self):
        # Entrada: tablero aplanado + dirección
        input_data = keras.layers.Input(shape=(10*10 + 4,))
        
        x = keras.layers.Dense(512, activation='relu')(input_data)
        x = keras.layers.Dense(256, activation='relu')(x)
        outputs = keras.layers.Dense(4)(x)  # 4 salidas para las acciones
        
        model = keras.models.Model(inputs=input_data, outputs=outputs)
        model.compile(optimizer='adam', loss='mean_squared_error')
        
        return model

    def evaluate(self, data, labels):
        # Evalúa la red neuronal en un conjunto de datos y establece el fitness
        self.fitness = self.model.evaluate(data, labels, verbose=0)[1]  # Suponiendo que el segundo valor es el accuracy




    # def predict_next_move(self, state):
    #     board = state['board']
    #     direction = state['direction']

    #     # Agrega la dirección actual al final de cada fila del tablero
    #     direction_number = DIRECTION_MAP[direction]

    #     for row in board:
    #         row.append(direction_number)

    #     # Convierte el tablero en un numpy array y lo reformatea para la entrada de la red neuronal
    #     board_np = np.array(board).reshape(1, BOARD_SIZE, BOARD_SIZE + 1, 1)
        
    #     # Normaliza la entrada
    #     board_np = board_np / 3.0

    #     predictions = self.model.predict(board_np, verbose=0)
    #     predicted_move = np.argmax(predictions[0])

    #     # Mapea el movimiento predicho de vuelta a su cadena de texto correspondiente
    #     direction_string = list(DIRECTION_MAP.keys())[list(DIRECTION_MAP.values()).index(predicted_move)]

    #     return direction_string
    
    def predict_next_move(self, state):
        board = state['board']
        direction = state['direction']
        
        # Convierte la dirección a one-hot encoding
        direction_vector = [0, 0, 0, 0]
        direction_vector[DIRECTION_MAP[direction]] = 1

        # Aplana el tablero y concatena con el vector de dirección
        flattened_board = np.array(board).flatten()
        input_data = np.concatenate((flattened_board, direction_vector))
        
        # Reformatea y normaliza la entrada para la red neuronal
        input_np = input_data.reshape(1, BOARD_SIZE * BOARD_SIZE + 4)
        input_np = input_np / 3.0
        
        # Predicción
        predictions = self.model.predict(input_np, verbose=0)
        predicted_move = np.argmax(predictions[0])
        
        # Mapea el movimiento predicho de vuelta a su cadena de texto correspondiente
        direction_string = list(DIRECTION_MAP.keys())[list(DIRECTION_MAP.values()).index(predicted_move)]

        return direction_string
    
