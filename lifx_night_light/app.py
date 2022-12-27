import os
from pathlib import Path
from typing import Tuple

from flask import Flask, render_template, request, jsonify
from flask.wrappers import Response
from crontab import CronTab  # type: ignore[import]
import yaml

app = Flask(__name__)

LIFX_CONF = Path(os.getenv("LIFX_CONF", "conf"))
CRON_FILE = LIFX_CONF / "cron.yml"
ARGS_FILE = LIFX_CONF / "args.yml"
LIFX_BIN = os.getenv("LIFX_BIN", "/usr/local/bin/lifx-cli")


def set_cron(days: str, time: str, duration: str) -> None:
    hour, minute = time.split(":")
    cron = CronTab(user="root")
    cron.remove_all(comment="wake")
    if days != "off":
        cmd = " ".join(
            [
                LIFX_BIN,
                "wake",
                f"--duration={duration}",
                "--steps=100",
                ">>/var/log/cron.log 2>&1",
            ]
        )
        job = cron.new(
            command=cmd,
            comment="wake",
        )
        job.minute.on(minute)
        job.hour.on(hour)
        if days == "all":
            job.dow.every(1)
        else:
            job.dow.on(1, 2, 3, 4, 5)
    cron.write()


def get_cron_config() -> Tuple[str, str, str]:
    with open(CRON_FILE, "r") as f:
        config = yaml.safe_load(f)
    app.logger.info(str(config))
    days = config["days"]
    time = config["time"]
    duration = config["duration"]
    return days, time, duration


def init_cron() -> None:
    days, time, duration = get_cron_config()
    set_cron(days, time, duration)


@app.route("/")
def index() -> str:
    days, time, duration = get_cron_config()
    return render_template("index.html", days=days, time=time, duration=duration)


@app.route("/api/update")
def update() -> Response:
    app.logger.info("Updating")
    days = request.args.get("days", "all")
    time = str(request.args.get("time"))
    duration = request.args.get("duration", "60")
    app.logger.warning(f"New wake: {days}, {time}, {duration}")

    with open(CRON_FILE, "w") as f:
        yaml.dump({"days": days, "time": time, "duration": duration}, f)
    set_cron(days, time, duration)

    return jsonify("Updated")


@app.route("/api/sleep")
def sleep() -> Response:
    duration = request.args.get("duration")
    app.logger.warning(f"Wind down for {duration} mins")
    args = {"scene": "sleep", "duration": duration, "steps": 60}
    with open(ARGS_FILE, "w") as f:
        yaml.dump(args, f)
    return jsonify("Sleep!")


init_cron()
