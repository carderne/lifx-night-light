import os
import time
from pathlib import Path

import yaml

from . import runner

LIFX_CONF = Path(os.getenv("LIFX_CONF", "conf"))
ARGS_FILE = LIFX_CONF / "args.yml"


def wait() -> None:
    print("Daemon started")
    while True:
        try:
            with open(ARGS_FILE) as f:
                a = yaml.safe_load(f)
            scene = str(a["scene"])
            duration = int(a["duration"])
            runner.main(scene, duration)
        except FileNotFoundError:
            pass
        finally:
            try:
                os.remove(ARGS_FILE)
            except FileNotFoundError:
                pass
            time.sleep(1)
