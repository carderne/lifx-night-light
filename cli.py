#!/usr/bin/env python3

from typer import Typer, Argument, Option

import lights

app = Typer(add_completion=False)

@app.command()
def main(
    scene: str = Argument(..., help="Name of scene in scenes.yml"),
    duration: float = Option(1, help="Duration in minutes"),
    steps: int = Option(100, help="Number of steps to use"),
    draw: bool = Option(False, help="Set to draw a plot and exit (no lighting)"),
):
    lights.runner.main(scene, duration, steps, draw)

if __name__ == "__main__":
    app()
