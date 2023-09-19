

let active = true
let snakeGames = [];
const boardCount = 21;
const tableWidth = 10;
const tableHeigth = 10;
let applePos = []

class SnakeGame {
    constructor(id) {
        this.id = id;

        this.snake = [{ x: 0, y: 2 }];  // La serpiente comienza en el centro
        
        this.direction = "RIGHT";
        this.score = 0;
        this.goodChoise = 0;
        this.turns = 0;
        this.gameOver = false;
        this.timeLeft = 40;
        this.food = applePos[this.score];
    }

    isAlive(){
        return !this.gameOver
    }

    advance(){
        if (!this.gameOver){
            this.snakeAdvance();
            if (!this.isSnakeDead()){
                this.drawBoard(); 
                this.incrementTurns();
            } 
            else{
                this.gameOver = true;
            }  
        }
    }

    drawBoard() {
        let id = 'board' + this.id;
        const boardElement = document.getElementById(id);
    
        boardElement.innerHTML = "";
        for (let y = 0; y < tableHeigth; y++) {
            for (let x = 0; x < tableWidth; x++) {
                const cellElement = document.createElement("div");
                cellElement.classList.add("cell");
    
                if (this.snake.some(segment => segment.x === x && segment.y === y)) {
                    //si es cabeza
                    if (this.snake[0].x === x && this.snake[0].y === y){
                        cellElement.classList.add("snake_head");
                        switch(this.direction){
                            case 'RIGHT':
                                cellElement.classList.add("right");
                                break;
                            case 'LEFT':
                                cellElement.classList.add("left");
                                break;
                            case 'UP':
                                cellElement.classList.add("up");
                                break;
                            case 'DOWN':
                                cellElement.classList.add("down");
                                break;
                        }
                        
                    }else{
                        cellElement.classList.add("snake_body");
                    }
                    
                } else if (this.food.x === x && this.food.y === y) {
                    cellElement.classList.add("food");
                }
                
                boardElement.appendChild(cellElement);
            }
        }
    
        document.getElementById("score" + this.id).innerText = this.score;
        document.getElementById("turns" + this.id).innerText = this.turns;
    }

    isSnakeDead(){
        let outOfBoard = this.snake[0].x >= tableHeigth || this.snake[0].x < 0 || this.snake[0].y >= tableHeigth || this.snake[0].y < 0;
        let isBittingItself = false;
        for (let i = 1; i < this.snake.length; i++){
            if (this.snake[0].x === this.snake[i].x && this.snake[0].y === this.snake[i].y){
                isBittingItself = true;
            }
        }
        return outOfBoard || isBittingItself || this.timeLeft == 0;
    }
    
    snakeAdvance(){
        let createSegment = this.snake[0].x == this.food.x && this.snake[0].y == this.food.y;
    
        let newSegment = {x: this.snake[this.snake.length - 1].x, y: this.snake[this.snake.length - 1].y};
        let lastSegment = {x: this.snake[0].x, y: this.snake[0].y};

        this.timeLeft--;

        function distancia(x1, y1, x2, y2) {
            return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        }

        let distanciaActual = distancia(this.snake[0].x, this.snake[0].y, this.food.x, this.food.y);
    
    
        switch(this.direction){
            case 'RIGHT':
                this.snake[0].x++;
                break;
            case 'LEFT':
                this.snake[0].x--;
                break;
            case 'UP':
                this.snake[0].y--;
                break;
            case 'DOWN':
                this.snake[0].y++;
                break;
        }

        let distanciaTrasMoverse = distancia(this.snake[0].x, this.snake[0].y, this.food.x, this.food.y);

        if (distanciaTrasMoverse < distanciaActual) this.goodChoise++;
    
        //AVANZAMOS EL RESTO DE SEGMENTOS
        for (let i = 1; i < this.snake.length; i++){
            let aux = {x: this.snake[i].x, y: this.snake[i].y};
            this.snake[i] = {x: lastSegment.x, y: lastSegment.y};
            lastSegment = {x: aux.x, y: aux.y};
        }
        if (createSegment){
            this.incrementScore();
            this.timeLeft = 40;
            this.snake.push(newSegment);
            this.food = applePos[this.score];
        }
    }
    
    // Suponiendo que en alguna parte de tu código incrementas el score y los turnos
    incrementScore() {
        this.score++;
    }
    
    incrementTurns() {
        this.turns++;
    }

    getGameState(){
        let board = [];
        for (let y = 0; y < tableHeigth; y++) {
            let line = [];
            for (let x = 0; x < tableWidth; x++) {
                line.push(0);
            }
            board.push(line);
        }

        board[this.snake[0].x][this.snake[0].y] = 1
        
        for (let i = 1; i < this.snake.length; i++){
            board[this.snake[i].x][this.snake[i].y] = 2
        }

        board[this.food.x][this.food.y] = 3


        let state = {
            id: this.id,
            direction: this.direction,
            board: board
        } 

        return state
    }

    async getNextMoveFromServer() {

        const url = "/next_snake_move/";
        try{
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    state: state
                })
            })

            const responseData = await response.json();
            let direction = responseData.next_move;
            switch(direction) {
                case 'RIGHT':
                    if(this.direction !== 'LEFT') this.direction = 'RIGHT';
                    break;
                case 'LEFT':
                    if(this.direction !== 'RIGHT') this.direction = 'LEFT';
                    break;
                case 'UP':
                    if(this.direction !== 'DOWN') this.direction = 'UP';
                    break;
                case 'DOWN':
                    if(this.direction !== 'UP') this.direction = 'DOWN';
                    break;
            }
        }
        catch (error){
            console.error('Error:', error);
        }     
    }
}

document.addEventListener("keydown", (event) => {
    switch(event.key) {
        case 'ArrowRight':
            if(snakeGames[0].direction !== 'LEFT') snakeGames[0].direction = 'RIGHT';
            break;
        case 'ArrowLeft':
            if(snakeGames[0].direction !== 'RIGHT') snakeGames[0].direction = 'LEFT';
            break;
        case 'ArrowUp':
            if(snakeGames[0].direction !== 'DOWN') snakeGames[0].direction = 'UP';
            break;
        case 'ArrowDown':
            if(snakeGames[0].direction !== 'UP') snakeGames[0].direction = 'DOWN';
            break;
    }
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // ¿Este cookie tiene el prefijo que buscamos?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function initSnakeGames(){
    //Crea los snakeGame
    snakeGames = []
    for (let i = 1; i <= boardCount; i++){
        snakeGames.push(new SnakeGame(i));
    }
}

async function getNextMovesFromServer(allGamesStates) {

    const url = "/next_snake_move/";
    try{
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                allGames: allGamesStates
            })
        })

        const responseData = await response.json();
        return responseData;
    }
    catch (error){
        active = false;
        console.error('Error:', error);
    }     
}

async function getNextGenFromServer(allGamesResults) {

    const url = "/next_snake_gen/";
    try{
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                allGames: allGamesResults
            })
        })

        const responseData = await response.json();
        return responseData;
    }
    catch (error){
        active = false;
        console.error('Error:', error);
    }     
}



// ###############loop del juego
async function gameLoop() {

    for (let i = 0; i < tableWidth * tableHeigth; i++){
        applePos.push({ x: Math.floor(Math.random() * tableWidth), y: Math.floor(Math.random() * tableHeigth) });
    }

    initSnakeGames();
    while(active) {
        let allGamesStates = [];
        snakeGames.forEach(snakeGame => {
            if (snakeGame.isAlive()){
                allGamesStates.push(snakeGame.getGameState());
            }
        })

        if (allGamesStates.length === 0){
            allGamesResults = [];
            snakeGames.forEach(snakeGame => {
                allGamesResults.push({'id': snakeGame.id, 'fitness': Math.pow(snakeGame.score, 2) + snakeGame.goodChoise });
                // allGamesResults.push({'id': snakeGame.id, 'fitness': snakeGame.score});
            })
            const response = await getNextGenFromServer(allGamesResults);

            initSnakeGames();
        }
        else{
            const response = await getNextMovesFromServer(allGamesStates);
            response.games.forEach( gameResponse => {
                snakeGames.forEach(snakeGame => {
                    if (gameResponse.id === snakeGame.id){
                        switch(gameResponse.next_move) {
                            case 'RIGHT':
                                if(snakeGame.direction !== 'LEFT') snakeGame.direction = 'RIGHT';
                                break;
                            case 'LEFT':
                                if(snakeGame.direction !== 'RIGHT') snakeGame.direction = 'LEFT';
                                break;
                            case 'UP':
                                if(snakeGame.direction !== 'DOWN') snakeGame.direction = 'UP';
                                break;
                            case 'DOWN':
                                if(snakeGame.direction !== 'UP') snakeGame.direction = 'DOWN';
                                break;
                        }
                    }
                })
            })
            snakeGames.forEach(snakeGame => { snakeGame.advance() })
        }
        
    }
}
gameLoop();