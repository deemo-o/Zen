from random import randint, choice

# initialize the grid with all 0s (no ships)
grid = [[0 for _ in range(10)] for _ in range(10)]

# sizes of the ships to be placed
sizes = [5, 4, 3, 3, 2, 2, 1]

# list to store the start and end coordinates of each ship
ships = []

# place the ships on the grid
for size in sizes:
    placed = False
    while not placed:
        # choose a random position and orientation (horizontal or vertical) for the ship
        row = randint(0, 9)
        col = randint(0, 9)
        orientation = choice(['horizontal', 'vertical'])

        # check if the ship fits on the grid at the chosen position and orientation
        fits = True
        if orientation == 'horizontal':
            if col + size > 10:
                fits = False
            else:
                for i in range(col, col+size):
                    if grid[row][i] != 0:
                        fits = False
                        break
        else:  # orientation == 'vertical'
            if row + size > 10:
                fits = False
            else:
                for i in range(row, row+size):
                    if grid[i][col] != 0:
                        fits = False
                        break

        # if the ship fits, place it on the grid and store its start and end coordinates
        if fits:
            start_coord = (row, col)
            if orientation == 'horizontal':
                end_coord = (row, col+size-1)
                for i in range(col, col+size):
                    grid[row][i] = 1
            else:  # orientation == 'vertical'
                end_coord = (row+size-1, col)
                for i in range(row, row+size):
                    grid[i][col] = 1
            ships.append((start_coord, end_coord))
            placed = True
