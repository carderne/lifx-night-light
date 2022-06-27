#!/usr/bin/env python3

import os
import time

import yaml

import lights


def wait():
    args_file = "args.yml"

    print("Daemon started")
    while True:
        try:
            with open(args_file) as f:
                a = yaml.safe_load(f)
            scene = str(a["scene"])
            duration = int(a["duration"])
            steps = int(a["steps"])
            lights.runner.main(scene, duration, steps)
        except FileNotFoundError:
            pass
        finally:
            try:
                os.remove(args_file)
            except FileNotFoundError:
                pass
            time.sleep(1)


if __name__ == "__main__":
    wait()
