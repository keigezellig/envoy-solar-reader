# Envoy Solar Reader

This application will retrieve data from Enlighten Envoy Solar micro inverters connected through an Enlighten Enphase Envoy Gateway.   
The data is then posted to a MQTT topic which can be used in a home automation setup. See below for my setup with Home Assistant

## Supported firmware
It *only* supports gateways with firmware 0.7x or greater (especially in local mode, see below) since the authentication mechanism has changed in comparison
with earlier firmware.

## Modes
The application currently only supports *local* mode which means it connects directly to the gateway in your network
In the future a *cloud* mode will be added which means it will retrieve the date through the [Enlighten API](https://developer-v4.enphase.com)

## What data is retrieved
Currently only the daily produced energy (in kWh) and the current power output (in W) for the whole array of inverters is returned.
In the future data for each individual inverter will also be retrieved.


## System requirements
- A Linux distribution (sorry, Windows isn't supported (yet))
- Python 3.10+ + tooling (pip, virtualenv)
- [Poetry](https://python-poetry.org/) - Package management tool for Python.


## Quick start
- Download and unzip the latest stable release from the 'Releases' (or if you want the latest and greatest, checkout the develop branch of this repository) to a directory.
- Go to this directory.
- Create a *config.yaml* file with your desired settings (see *config_example.yaml* for the possible settings and their descriptions)
- Run `poetry install` to install the application and all its dependencies. It will create a virtual environment
- Run `poetry run envoy_solar_reader` to start the application with the default command line options. 
- The data is now retrieved every interval as specified in the config and posted to a MQTT topic *envoy/production*

## Command line options
These can also be shown with `poetry run envoy_solar_reader -h`
```
usage: envoy_solar_reader [-h] [--config CONFIG] [--mode {local,cloud}] [--loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

options:
  -h, --help            show this help message and exit
  --config CONFIG       Full path to config file. If left empty, program will try to load config.yaml from the current directory
  --mode {local,cloud}  Use api on local device or use cloud based api
  --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Minimum loglevel

```

## Example setup for HomeAssistant
This is how my setup with Home Assistant works:
- In Home Assistant install the MQTT integration, so that there is a MQTT broker active on the HA instance.
- Install the Envoy Solar Reader on a separate device in your network (i had a spare Raspberry Pi lying around) and (optionally) create
  a systemd service to start the application when booting the device. (see below)
- Contents of *config.yaml*:
```yaml
mqtt:
  host: <homeassistant host/ip>
  port: 1883
  username: homeassistant
  password: <mqtt broker password>
  report_interval_seconds: 300

local:
  envoy_host: <ip of envoy gateway>
  envoy_user: <enphase username>
  envoy_password: <enphase password>
  envoy_serial: <envoy gateway serialnumber>
  ```
- Create a sensor definition in HA as follows:

```yaml
mqtt:
  sensor:
    - name: "Solar energy produced today"
      state_class: total_increasing         # IMPORTANT IF YOU WANT TO USE THIS IN THE ENERGY DASHBOARD
      device_class: energy                  # IMPORTANT IF YOU WANT TO USE THIS IN THE ENERGY DASHBOARD
      state_topic: envoy/production
      unit_of_measurement: "kWh"
      value_template: "{{ value_json.energyProducedTodayInKwh }}"
      last_reset_value_template: "1970-01-01T00:00:00+00:00"
      expire_after: 600
    
    - name: "Current total solar power"
      state_class: measurement
      device_class: energy
      state_topic: envoy/production
      unit_of_measurement: "kW"
      value_template: "{{ value_json.currentTotalPowerInWatts |float / 1000 }}"
      expire_after: 600

```
- Configure the energy dashboard with the `Solar energy produced today` sensor.
- Put the `Current total solar power` on a dashboard

Some screenshots:

![screenshot_energy_dashboard](screenshot_energy_dashboard.png)

![screenshot_dashboard_with_current_power.png](screenshot_dashboard_with_current_power.png)


### Systemd service
I created a systemd service to start the application after reboot. See *systemd* directory.   
To set this up: 
- Modify the *envoy_solar_reader.service* to your liking. (see [here](https://www.digitalocean.com/community/tutorials/understanding-systemd-units-and-unit-files)
  and [here](https://medium.com/codex/setup-a-python-script-as-a-service-through-systemctl-systemd-f0cc55a42267) for more in-depth information)
- Copy the service definition file to `/etc/systemd/system`
- Execute `sudo systemctl daemon-reload` to reload the systemd daemon
- Execute `sudo systemctl enable envoy_solar_reader.service` to enable restarting of the service after a reboot
- Execute `sudo systemctl start envoy_solar_reader.service` to start the application/service
- Logs can be viewed by executing `sudo journalctl -u envoy_solar_reader.service`


## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`envoy_solar_reader` was created by Maarten Joosten. It is licensed under the terms of the MIT license.

## Credits

`envoy_solar_reader` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
