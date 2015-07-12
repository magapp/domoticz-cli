domoticz-cli
============

This simple tool is a CLI for [Domoticz](http://www.domoticz.com/).

You can power on/off light switches, list sensor values and much more. Domoticz-cli can also produce Graphite compatible output or report directly to [Librato](http://www.librato.com|Librato).

```
usage: domoticz-cli.py [-h] [--host HOST] [--port PORT] [--debug]
                       [--list-switches] [--list-sensors]
                       [--list-sensors-graphite] [--list-sensors-librato]
                       [--report-prefix NAME] [--list-scenes] [--list-groups]
                       [--toggle-switch NAME] [--run-scene NAME]
                       [--get-sunrise] [--librato-user LIBRATO_USER]
                       [--librato-token LIBRATO_TOKEN]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host to connect to
  --port PORT           Port to connect to
  --debug               Display more debug information
  --list-switches       List all switches and their state
  --list-sensors        List all sensors and their value
  --list-sensors-graphite
                        List all sensors in Graphite readable format
  --list-sensors-librato
                        Report all sensors to Librato
  --report-prefix NAME  If set, use this string as prefix for all Graphite and
                        Librato data
  --list-scenes         List all scenes
  --list-groups         List all groups
  --toggle-switch NAME  Toggle a switch
  --run-scene NAME      Run a scene
  --get-sunrise         Get and display time for sunrise and sunset
  --librato-user LIBRATO_USER
                        Librato user name. If also Librato token is set,
                        report sensors to Librato.
  --librato-token LIBRATO_TOKEN
                        Librato token. If also Librato user is set, report
                        sensors to Librato.
```

Examples
========

```
$ domoticz-cli.py  --list-sensors
Utebelysning entre             4.8 Watt                  2015-07-12 22:47:15
Utelampa vedbod                7.9 Watt                  2015-07-12 22:46:28
Kontor                         21.1 C, 59 %              2015-07-12 22:43:42
```

```
$ domoticz-cli.py  --librato-user xx --librato-token yy --list-sensors-librato --report-prefix villan.domoticz
Reported 33 values to Librato.
```

Installation
============

```
pip install requests
pip install argparse
# optional:
pip install librato
```

