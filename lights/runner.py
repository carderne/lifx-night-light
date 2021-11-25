import time
from pathlib import Path
from typing import List, Tuple

from lifxlan import LifxLAN, Light
from lifxlan.errors import WorkflowException
from numpy import linspace
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import yaml

maxint = 65535

def converter(omin=0, omax=maxint, imin=0, imax=100):
    return lambda x: omin + int((max(min(x, imax), imin) / imax) * (omax - omin))


def fix_range(val: list) -> list:
    if isinstance(val, int):
        return [val, val]
    elif len(val) == 0:
        raise ValueError("Color lists should have at least one value")
    elif len(val) == 1:
        return val + val
    return val


def load_scene(scene: str, steps: int) -> Tuple[list, str]:
    with open("scenes.yml") as f:
        vals = yaml.safe_load(f)[scene]

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


def plot(path: Path, colors: List[List[float]]) -> None:
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


def main(
    scene: str,
    duration: float,
    steps: int,
    draw: bool = False,
):
    colors, after = load_scene(scene, steps)
    if draw:
        plot(f"{scene}.png", colors)
        return

    if steps * 0.02 > duration * 60:
        print("Warning: fade may over-run due to LIFX lag")
        print("Consider a longer duration or fewer steps")

    with open("device.yml") as f:
        device_config = yaml.safe_load(f)

    try:
        bulb = Light(device_config["mac"], device_config["ip"])
        bulb.get_power()  # check that bulb works
    except (TypeError, KeyError, ValueError, WorkflowException):
        print("Device not/wrongly configured, getting first device on network")
        bulb = LifxLAN(1).get_lights()[0]
        device_config = {"ip": bulb.get_ip_addr(), "mac": bulb.get_mac_addr()}
        with open("device.yml", "w") as f:
            yaml.dump(device_config, f)

    print("Starting lighting")
    bulb.set_power("on")
    for color in colors:
        start = time.time()
        bulb.set_color(color)
        lag = time.time() - start
        time.sleep(max(0, duration * 60 / steps - lag))
    bulb.set_power(after)
    print("Done lighting")
