import time
import statistics
import random
import arcade

from map import Map, GridCell, build_navmesh
from gameview import GameView
from constants import TILE_SIZE


def make_grid(width: int, height: int) -> tuple[tuple[GridCell, ...], ...]:
    grid = [[GridCell.GRASS for _ in range(width)] for _ in range(height)]

    # Quelques obstacles pour rendre le navmesh réaliste
    for y in range(0, height, 5):
        for x in range(width // 4, 3 * width // 4):
            grid[height - 1 - y][x] = GridCell.BUSH

    return tuple(tuple(row) for row in grid)


def benchmark_map_loading() -> None:
    sizes = [10, 20, 40, 80, 120]
    density = 3
    repeats = 5

    print("Benchmark chargement map")
    print("size,cells,time")

    for size in sizes:
        times = []

        for _ in range(repeats):
            grid = make_grid(size, size)

            start = time.perf_counter()
            Map(
                width=size,
                height=size,
                player_start_x=0,
                player_start_y=0,
                grid=grid,
                navmesh=build_navmesh(size, size, grid, density=density),
                switches=(),
                gates=(),
            )
            end = time.perf_counter()

            times.append(end - start)

        print(f"{size},{size * size},{statistics.mean(times)}")


def make_enemy_map(enemy_count: int, width: int = 40, height: int = 40) -> Map:
    grid = [[GridCell.GRASS for _ in range(width)] for _ in range(height)]

    grid[height - 1 - 1][1] = GridCell.GRASS

    rng = random.Random(0)
    placed = 0

    while placed < enemy_count:
        x = rng.randrange(2, width - 2)
        y = rng.randrange(2, height - 2)

        if grid[height - 1 - y][x] == GridCell.GRASS:
            grid[height - 1 - y][x] = GridCell.SLIME
            placed += 1

    grid_tuple = tuple(tuple(row) for row in grid)

    return Map(
        width=width,
        height=height,
        player_start_x=1,
        player_start_y=1,
        grid=grid_tuple,
        navmesh=build_navmesh(width, height, grid_tuple),
        switches=(),
        gates=(),
    )



def benchmark_on_update() -> None:
    enemy_counts = [1, 5, 10, 20, 40, 80]
    frames = 300

    print("Benchmark on_update")
    print("enemies,time_per_frame")

    window = arcade.Window(800, 600, visible=False)

    for enemy_count in enemy_counts:
        game_map = make_enemy_map(enemy_count)
        view = GameView(game_map)
        window.show_view(view)

        start = time.perf_counter()

        for _ in range(frames):
            view.on_update(1 / 60)

        end = time.perf_counter()

        average_time = (end - start) / frames
        print(f"{enemy_count},{average_time}")

    window.close()


def main() -> None:
    benchmark_map_loading()
    print()
    benchmark_on_update()


if __name__ == "__main__":
    main()
