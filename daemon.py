#!/usr/bin/env python3

import os
import time

import yaml

import lights

def wait():
    args_file = "args.yml"

    print("Daemon started")
    while True:
        print("Waiting...")
        try:
            with open(args_file) as f:
                a = yaml.safe_load(f)
            scene = a["scene"]
            duration = a["duration"]
            steps = a["steps"]
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
