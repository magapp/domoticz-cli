#!/usr/bin/env python
# -*- coding: utf-8 -*-
# magnus@appelquist.name

import requests, json, argparse, sys, time, datetime

import codecs
UTF8Writer = codecs.getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)

parser = argparse.ArgumentParser()
parser.add_argument("--host", help="Host to connect to", default="localhost")
parser.add_argument("--port", type=int, help="Port to connect to", default=8080)
parser.add_argument("--debug", action="store_true", help="Display more debug information")
parser.add_argument("--list-switches", action="store_true", help="List all switches and their state")
parser.add_argument("--list-sensors", action="store_true", help="List all sensors and their value")
parser.add_argument("--list-sensors-graphite", action="store_true", help="List all sensors in Graphite readable format")
parser.add_argument("--list-sensors-librato", action="store_true", help="Report all sensors to Librato")
parser.add_argument("--report-prefix", metavar='NAME', required=False, help="If set, use this string as prefix for all Graphite and Librato data")
parser.add_argument("--list-scenes", action="store_true", help="List all scenes")
parser.add_argument("--list-groups", action="store_true", help="List all groups")
parser.add_argument("--toggle-switch", action="store", help="Toggle a switch", metavar='NAME')
parser.add_argument("--run-scene", action="store", help="Run a scene", metavar='NAME')
parser.add_argument("--get-sunrise", action="store_true", help="Get and display time for sunrise and sunset")
parser.add_argument("--librato-user", help="Librato user name. If also Librato token is set, report sensors to Librato.", required=False)
parser.add_argument("--librato-token", help="Librato token. If also Librato user is set, report sensors to Librato.", required=False)

args = parser.parse_args()

debug = args.debug

def _get_request(cmd):
    global debug
    url = "http://"+args.host+":"+str(args.port)+"/json.htm?"+cmd
    if debug: print url
    r = requests.get(url)
    if r.status_code != 200 or r.json()["status"] != "OK":
        print "Problem talking with domoticz, exit..."
        print r.status_code
        print r.text
        sys.exit(1)
    return r.json()

if args.get_sunrise:
    data = _get_request("type=command&param=getSunRiseSet")
    print "Sunrise is at "+data["Sunrise"]+" and sunset is at "+data["Sunset"]

if args.list_sensors:
    data = _get_request("type=devices&filter=all&used=true&order=Name")

    for result in data["result"]:
        if result["Type"] not in ["Lighting 2","Scene", "Group"]:
            print u"%-30s %-20s     %20s" % (result["Name"], result["Data"], result["LastUpdate"])

if args.list_sensors_graphite:
    data = _get_request("type=devices&filter=all&used=true&order=Name")

    for result in data["result"]:

        graphite_path = result["Name"].lower().replace(" ","-").encode("ascii","ignore")
        #graphite_path = result["Name"].lower().replace(" ","-")
        if args.report_prefix:
            graphite_path = args.report_prefix+"."+graphite_path
        timestamp = int(time.mktime(datetime.datetime.strptime(result["LastUpdate"], "%Y-%m-%d %H:%M:%S").timetuple()))

        if result["Type"] == "Temp":
            print u"%s.temperature %.1f %d" % (graphite_path, result["Temp"], timestamp)

        if result["Type"] == "Temp + Humidity":
            print u"%s.temperature %.1f %d" % (graphite_path, result["Temp"], timestamp)
            print u"%s.humidity %.1f %d" % (graphite_path, result["Humidity"], timestamp)

        if result["Type"] == "Usage":
            print u"%s.energy %.1f %d" % (graphite_path, float(result["Data"].split(" ")[0]), timestamp)

        if result["Type"] == "Value":
            print u"%s.value %d %d" % (graphite_path, int(result["Data"]), timestamp)

        if result["Type"] == "RFXMeter":
            print u"%s.counter %d %d" % (graphite_path, int(result["Data"].split(" ")[0].replace(".","")), timestamp)

if args.list_sensors_librato and args.librato_user and args.librato_token:
    import librato

    librato_api = librato.connect(args.librato_user, args.librato_token)
    q = librato_api.new_queue()
    q.add('temperature', 23.1, source='dowstairs')
    q.add('num_requests', 100, type='counter', source='server1')
    q.add('num_requests', 102, type='counter', source='server2')

    data = _get_request("type=devices&filter=all&used=true&order=Name")

    nbr_values = 0
    for result in data["result"]:

        librato_path = result["Name"].lower().replace(" ","-").encode("ascii","ignore")
        if args.report_prefix:
            librato_path = args.report_prefix+"."+librato_path

        if result["Type"] == "Temp":
            q.add(u"%s.temperature" % librato_path, result["Temp"])
            nbr_values += 1

        if result["Type"] == "Temp + Humidity":
            q.add(u"%s.temperature" % librato_path, result["Temp"])
            q.add(u"%s.humidity" % librato_path, result["Temp"])
            nbr_values += 2

        if result["Type"] == "Usage":
            q.add(u"%s.energy" % librato_path, float(result["Data"].split(" ")[0]))
            nbr_values += 1

        if result["Type"] == "Value":
            q.add(u"%s.value" % librato_path, int(result["Data"]))
            nbr_values += 1

        if result["Type"] == "RFXMeter":
            q.add(u"%s.counter" % librato_path, float(result["Data"].split(" ")[0].replace(".","")), type = "counter")
            nbr_values += 1

    print "Reported %d values to Librato." % nbr_values
    q.submit()

if args.list_sensors_librato and (not args.librato_user or not args.librato_token):
    print "If reporting metrics to Librato you must also provide --librato-user and --librato-token"
    sys.exit(1)

if args.list_switches:
    data = _get_request("type=devices&filter=all&used=true&order=Name")

    for result in data["result"]:
        if result["Type"] == "Lighting 2":
            if debug:
                print u"%-30s %-20s     %20s idx: %s" % (result["Name"], result["Data"], result["LastUpdate"], str(result["idx"]))
            else:
                print u"%-30s %-20s     %20s" % (result["Name"], result["Data"], result["LastUpdate"])

if args.list_scenes or args.list_groups:
    data = _get_request("type=scenes")

    for result in data["result"]:
        if args.list_scenes and result["Type"] == "Scene" or args.list_groups and result["Type"] == "Group":
            if debug:
                print u"%-30s %-20s     %20s idx: %s" % (result["Name"], result["Status"], result["LastUpdate"], str(result["idx"]))
            else:
                print u"%-30s %-20s     %20s" % (result["Name"], result["Status"], result["LastUpdate"])


if args.toggle_switch:
    data = _get_request("type=devices&filter=all&used=true&order=Name")
    for result in data["result"]:
        if result["Type"] == "Lighting 2":
            if result["Name"] == args.toggle_switch.decode("utf-8"):
                print "Switch is "+result["Status"]+", toggling..."
                if result["Status"] == "On":
                    data = _get_request("type=command&param=switchlight&idx=%d&switchcmd=Off" % int(result["idx"]))
                else:
                    data = _get_request("type=command&param=switchlight&idx=%d&switchcmd=On" % int(result["idx"]))
    
if args.run_scene:
    data = _get_request("type=scenes")

    for result in data["result"]:
        if args.run_scene.decode("utf-8") == result["Name"]:
            data = _get_request("type=command&param=switchscene&idx=%d&switchcmd=On" % int(result["idx"]))
    
