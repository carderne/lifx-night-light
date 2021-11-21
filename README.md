# lifx-transitions
Simple light transitions (wake-up, wind-down) for LIFX, using [lifxlan](https://github.com/mclarkk/lifxlan).

My [wake-up light](https://rdrn.me/wake-up-light/) became a bit of a fire hazard, so I gave up and bought a [LIFX Colour](https://lifxshop.co.uk/products/lifx-colour-e27).

But relying on the cloud for lights seems silly, so I blocked it from the internet and wrote this script to control it with my Raspberry Pi.

## Installation
```
git clone git@github.com:carderne/lifx-transitions.git
cd lifx-transitions
pip install -r requirements.txt
```

## Configuration
Create a YAML config file something like the example below with a list of values for each of these:
- `hue` ranges from 0 to 360 in a [color wheel](https://upload.wikimedia.org/wikipedia/commons/a/ad/HueScale.svg)
- `sat` (saturation) from 0 to 100
- `bri` (brightness) from 0 to 100
- `kel` (color temperature) from 0 to 100, will be translated to the range 2500K - 9000K
- `after`: what to do once the transition ends, either 'on' or 'off'

Values will be linearly interpolated so you can provide as many or as few as you like for each variable.

```yaml
hue: [45, 45, 45, 30, 30, 15, 15, 15, 0, 0, 0]
sat: [30, 70]
bri: [20, 15, 10, 5, 4, 3, 2, 1, 0]
kel: 20    # can just provide a constant like this
after: on  # optional, defaults to on
```

There are two more examples in [wake.yml](wake.yml) and [sleep.yml](sleep.yml).

## Running
See help output:
```bash
./run.py --help
```

To run, choose a config file and duration (in minutes):
```bash
./run.py wake.yaml 10
```
