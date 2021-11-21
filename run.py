#!/usr/bin/env python3

import time
from pathlib import Path
from typing import List

from lifxlan import LifxLAN
from numpy import linspace
from scipy.interpolate import interp1d
from typer import Typer, Argument, Option
import matplotlib.pyplot as plt
import yaml

app = Typer(add_completion=False)
maxint = 65535


def converter(omin=0, omax=maxint, imin=0, imax=100):
    return lambda x: omin + int((max(min(x, imax), imin) / imax) * (omax - omin))


def fix_range(val: List):
    if isinstance(val, int):
        return [val, val]
    elif len(val) == 0:
        raise ValueError("Color lists should have at least one value")
    elif len(val) == 1:
        return val + val
    return val


def load_scheme(scheme, steps):
    with open(scheme) as f:
        vals = yaml.safe_load(f)

    after = vals.pop("after", "on")
    for k, v in vals.items():
        vals[k] = fix_range(v)

    hue = interp1d(linspace(0, 100, len(vals["hue"])), vals["hue"])
    sat = interp1d(linspace(0, 100, len(vals["sat"])), vals["sat"])
    bri = interp1d(linspace(0, 100, len(vals["bri"])), vals["bri"])
    kel = interp1d(linspace(0, 100, len(vals["kel"])), vals["kel"])

    con = converter()
    conhue = converter(imax=360)
    conkel = converter(omin=2500, omax=9000)

    xs = (100 * s / steps for s in range(steps + 1))
    colors = ([conhue(hue(x)), con(sat(x)), con(bri(x)), conkel(kel(x))] for x in xs)
    return colors, after


def plot(path: Path, colors: List[List[float]]):
    with plt.xkcd():
        plt.rcParams["font.family"] = "sans"
        fig = plt.figure()
        ax = fig.add_axes((0.1, 0.2, 0.8, 0.7))
        ax.spines.right.set_color("none")
        ax.spines.top.set_color("none")
        ax.set_xticks([])
        ax.set_yticks([0, maxint])
        ax.set_yticklabels(["0", "max"])
        ax.set_ylim([0, maxint])

        colors = list(colors)
        plt.plot([c[0] for c in colors], label="hue")
        plt.plot([c[1] for c in colors], label="saturation")
        plt.plot([c[2] for c in colors], label="brightness")
        plt.plot([c[3] * maxint / 9000 for c in colors], label="temperature")

        ax.set_xlabel("time")
        ax.set_ylabel("value")
        plt.legend(loc="upper left")
        plt.savefig(path)
        print(f"Chart saved at {path}")


@app.command()
def main(
    scheme: Path = Argument(..., help="Path to scheme file"),
    duration: float = Option(3, help="Duration in minutes"),
    steps: int = Option(10000, help="Number of steps to use"),
    draw: bool = Option(False, help="Set to draw a plot and exit (no lighting)"),
):
    scheme = Path(scheme)
    colors, after = load_scheme(scheme, steps)
    if draw:
        plot(f"{scheme.stem}.png", colors)
        return

    if steps * 0.02 > duration * 60:
        print("Warning: fade may over-run due to LIFX lag")
        print("Consider a longer duration or fewer steps")

    lifx = LifxLAN(1)
    devices = lifx.get_lights()
    bulb = devices[0]

    bulb.set_power("on")
    for color in colors:
        start = time.time()
        bulb.set_color(color)
        lag = time.time() - start
        time.sleep(max(0, duration * 60 / steps - lag))
    bulb.set_power(after)


if __name__ == "__main__":
    app()
