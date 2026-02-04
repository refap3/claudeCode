import random
import os

# Grid size
GRID_SIZE = 50

# Density of alive cells (30%)
ALIVE_DENSITY = 0.3

def initialize_grid():
    grid = []
    for _ in range(GRID_SIZE):
        row = [random.random() < ALIVE_DENSITY for _ in range(GRID_SIZE)]
        grid.append(row)
    return grid

def print_grid(grid):
    os.system('cls' if os.name == 'nt' else 'clear')
    for row in grid:
        print(" ".join(['O' if cell else '.' for cell in row]))

def count_neighbors(grid, x, y):
    count = 0
    for i in range(max(0, x-1), min(GRID_SIZE, x+2)):
        for j in range(max(0, y-1), min(GRID_SIZE, y+2)):
            if (i != x or j != y) and grid[i][j]:
                count += 1
    return count

def next_generation(grid):
    new_grid = [[False] * GRID_SIZE for _ in range(GRID_SIZE)]
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            alive_neighbors = count_neighbors(grid, i, j)
            if grid[i][j]:
                if alive_neighbors < 2 or alive_neighbors > 3:
                    new_grid[i][j] = False
                else:
                    new_grid[i][j] = True
            else:
                if alive_neighbors == 3:
                    new_grid[i][j] = True
    return new_grid

def main():
    grid = initialize_grid()
    while True:
        print_grid(grid)
       
        grid = next_generation(grid)

if __name__ == "__main__":
    main()