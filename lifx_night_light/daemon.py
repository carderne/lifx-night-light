import os
import time

import yaml

from . import runner


def wait() -> None:
    args_file = "args.yml"

    print("Daemon started")
    while True:
        try:
            with open(args_file) as f:
                a = yaml.safe_load(f)
            scene = str(a["scene"])
            duration = int(a["duration"])
            steps = int(a["steps"])
            runner.main(scene, duration, steps)
        except FileNotFoundError:
            pass
        finally:
            try:
                os.remove(args_file)
            except FileNotFoundError:
                pass
            time.sleep(1)
