import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml
from lifxlan import LifxLAN, Light  # type: ignore[import]
from lifxlan.errors import WorkflowException  # type: ignore[import]
from numpy import linspace
from scipy.interpolate import interp1d  # type: ignore[import]

maxint = 65535

LIFX_CONF = Path(os.getenv("LIFX_CONF", "conf"))
SCENES_FILE = LIFX_CONF / "scenes.yml"
DEVICE_FILE = LIFX_CONF / "device.yml"


def converter(
    omin: int = 0, omax: int = maxint, imin: int = 0, imax: int = 100
) -> Callable[[int], int]:
    return lambda x: omin + int((max(min(x, imax), imin) / imax) * (omax - omin))


def fix_range(val: list | int) -> list[int]:
    if isinstance(val, int):
        return [val, val]
    elif len(val) == 0:
        raise ValueError("Color lists should have at least one value")
    elif len(val) == 1:
        return val + val
    return val


Color = tuple[int, int, int, int]
ColorSeq = list[Color]


@dataclass
class Config:
    colors: ColorSeq
    after: str
    off_after: int = -1


def load_scene(scene: str, steps: int) -> Config:
    with open(SCENES_FILE) as f:
        vals = yaml.safe_load(f)[scene]

    after = vals.pop("after", "on")
    off_after = int(vals.pop("after", -1))

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
    colors = [(conhue(hue(x)), con(sat(x)), con(bri(x)), conkel(kel(x))) for x in xs]

    config = Config(colors, after, off_after)
    return config


def plot(path: Path, colors: ColorSeq) -> None:
    import matplotlib.pyplot as plt  # type: ignore[import]

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


def retry(func: Callable, arg: Color | str, max_retries: int = 1) -> None:
    retries = 0
    while True:
        try:
            func(arg)
            return
        except WorkflowException:
            pass
        if retries >= max_retries:
            return
        retries += 1


def main(
    scene: str,
    duration: float,
    steps: int,
    draw: bool = False,
) -> None:
    config = load_scene(scene, steps)
    if draw:
        plot(Path(f"{scene}.png"), config.colors)
        return

    if steps * 0.02 > duration * 60:
        print("Warning: fade may over-run due to LIFX lag")
        print("Consider a longer duration or fewer steps")

    with open(DEVICE_FILE) as f:
        device_config = yaml.safe_load(f)

    try:
        bulb = Light(device_config["mac"], device_config["ip"])
        bulb.get_power()  # check that bulb works
    except (TypeError, KeyError, ValueError, WorkflowException):
        print("Device not/wrongly configured, getting first device on network")
        try:
            bulb = LifxLAN(1).get_lights()[0]
            device_config = {"ip": bulb.get_ip_addr(), "mac": bulb.get_mac_addr()}
            with open(DEVICE_FILE, "w") as f:
                yaml.dump(device_config, f)
        except IndexError:
            print("Couldn't find any device on network")
            exit()

    print("Starting lighting")
    retry(bulb.set_power, "on")
    overall_start = time.time()
    for color in config.colors:
        start = time.time()
        retry(bulb.set_color, color)

        if (time.time() - overall_start) // 60 >= duration:
            print("Ran out of time, set to last colour and quit")
            retry(bulb.set_color, config.colors[-1])
            break

        lag = time.time() - start
        sleep = max(0, duration * 60 / steps - lag)
        time.sleep(sleep)
    retry(bulb.set_power, config.after)

    if config.off_after >= 0:
        time.sleep(config.off_after * 60)
        retry(bulb.set_power, "off")
    print("Done lighting")
