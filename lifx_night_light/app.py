from flask import Flask, render_template, request, jsonify
from crontab import CronTab
import yaml

app = Flask(__name__)


config_file = "cron.yml"
args_file = "args.yml"
venv_loc = "/home/chris/lifx/venv/bin"


@app.route("/")
def index():
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    app.logger.info(str(config))
    days = config["days"]
    time = config["time"]
    duration = config["duration"]
    return render_template("index.html", days=days, time=time, duration=duration)


@app.route("/api/update")
def update():
    app.logger.info("Updating")
    days = request.args.get("days")
    time = request.args.get("time")
    duration = request.args.get("duration")
    app.logger.warning(f"New wake: {days}, {time}, {duration}")

    with open(config_file, "w") as f:
        yaml.dump({"days": days, "time": time, "duration": duration}, f)

    hour, minute = time.split(":")

    cron = CronTab(user=True)
    cron.remove_all(comment="wake")
    if days != "off":
        cmd = " ".join(
            [
                f"{venv_loc}/lifx-cli",
                "wake",
                f"--duration={duration}",
                "--steps=100",
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

    return jsonify("Updated")


@app.route("/api/sleep")
def sleep():
    duration = request.args.get("duration")
    app.logger.warning(f"Wind down for {duration} mins")
    args = {"scene": "sleep", "duration": duration, "steps": 60}
    with open(args_file, "w") as f:
        yaml.dump(args, f)
    return jsonify("Sleep!")
