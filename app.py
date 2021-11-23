import os
import json
from subprocess import run

from flask import Flask, render_template, request, jsonify
from crontab import CronTab
import yaml

app = Flask(__name__)


config_file = "config.json"


@app.route("/")
def index():
    with open(config_file, "r") as f:
        config = json.load(f)
    days = config["days"]
    time = config["time"]
    duration = config["duration"]
    return render_template("index.html", days=days, time=time, duration=duration)


@app.route("/api/update", methods=["POST"])
def update():
    print("Updating")
    values = request.get_json()
    days = values.get("days")
    time = values.get("time")
    duration = values.get("duration")

    with open(config_file, "w") as f:
        json.dump({"days": days, "time": time, "duration": duration}, fp=f)

    hour, minute = time.split(":")

    cron = CronTab(user=True)
    cron.remove_all(comment="wake")
    if days != "off":
        job = cron.new(
            command=f"/home/pi/lifx/venv/bin/python /home/pi/lifx/run.py /home/pi/lifx/wake.yml --duration={duration}",
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

@app.route("/api/sleep", methods=["POST"])
def sleep():
    cmd = [
        "/home/pi/lifx/venv/bin/python",
        "/home/pi/lifx/run.py",
        "/home/pi/lifx/sleep.yml",
        "--duration=30",
        "--steps=500",
    ]
    run(cmd, text=True, capture_output=True)
    print(p.stdout)
    return jsonify("Sleep!")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
