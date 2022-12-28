from typer import Typer, Argument, Option

from . import runner

app = Typer(add_completion=False)


@app.command()
def main(
    scene: str = Argument(..., help="Name of scene in scenes.yml"),
    duration: float = Option(1, help="Duration in minutes"),
    steps_per_min: int = Option(100, help="Number of steps per minute"),
    draw: bool = Option(False, help="Set to draw a plot and exit (no lighting)"),
) -> None:
    runner.main(scene, duration, steps_per_min, draw)


def cli() -> None:
    app()
