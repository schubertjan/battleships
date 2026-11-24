# How to use
If you want to retrain the model
`python -m simulate_games --games 200000 --db "battleship.db"`
`python -m train`

If you just want to play
`python -m play --game current-game.csv --fleet_sunk '{"Battleship": 0, "Cruiser": 0, "Destroyer": 0, "Submarine": 0, "PatrolBoat": 0}'`
Mark the matrix in `current-game.csv` (0=not fired yet, 1=miss, 2=hit)
