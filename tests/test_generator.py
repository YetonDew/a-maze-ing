from a_maze_ing.generator import MazeGenerator


def test_generate_small_maze():
    gen = MazeGenerator(5, 5, (0, 0), (4, 4), seed=42, perfect=True)
    maze = gen.generate()

    assert maze.width == 5
    assert maze.height == 5
    assert len(maze.walls) == 5
    assert len(maze.solution) >= 2
