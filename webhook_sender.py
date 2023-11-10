#!/usr/bin/python3

"""
------------------------------------------------------------------------------
Copyright (c) 2023 SUSE LLC

This program is free software; you can redistribute it and/or modify it under
the terms of version 3 of the GNU General Public License as published by the
Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, contact SUSE Linux GmbH.

------------------------------------------------------------------------------
Author: Thomas Schlosser <thomas.schlosser@suse.com>

A simple webhook sender which should similate sending prometheus alerts.
It only sends two older captured webhook posts I've captured with https://webhook.site .

Usages:

 python3 webhook_sender.py -t firing
 python3 webhook_sender.py -t resolved

The sending data are a copy of a real alert comming from the following prometheus alert rule:
(/etc/prometheus/rules/rules.yaml --> see also: https://github.com/schlosstom/GrafHana/ )

  - name: Wrong MTU on hana01
    rules:
      # To test the alert simply do:
      # docker exec -it hana01 /bin/bash
      # ip link set mtu 9000 dev lo
      # Default is: 65536
      - alert: mtu
        expr: node_network_mtu_bytes{device="lo"} == 9000
        for: 1m
        labels:
        annotations:
          title: MTU has been changed
          description:  MTU has been changed to 9000


"""

import requests
import json
import argparse

parser = argparse.ArgumentParser(description='Webhook sender for testing')
parser.add_argument('-t','--type', help='Given the type of alert (firing/resolved)', required=True)
args = vars(parser.parse_args())

webhook_url = "http://192.168.1.55:8080/webhook"

if args['type'] == 'firing':
    data = {'receiver': 'webhook', 'status': 'firing', 'alerts': [{'status': 'firing', 'labels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'annotations': {'description': 'MTU has been changed to 9000', 'title': 'MTU has been changed'}, 'startsAt': '2023-11-08T08:05:01.304Z', 'endsAt': '0001-01-01T00:00:00Z', 'generatorURL': 'http://85a4e3b559fe:9090/graph?g0.expr=node_network_mtu_bytes%7Bdevice%3D%22lo%22%7D+%3D%3D+9000&g0.tab=1', 'fingerprint': 'f56905cb7236a325'}], 'groupLabels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'commonLabels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'commonAnnotations': {'description': 'MTU has been changed to 9000', 'title': 'MTU has been changed'}, 'externalURL': 'http://c287739b59a5:9093', 'version': '4', 'groupKey': '{}:{alertname="mtu", device="lo", instance="hana01:9100", job="prometheus", monitor="GrafHana-monitor"}', 'truncatedAlerts': 0}

if args['type'] == 'resolved':
    data = {'receiver': 'webhook', 'status': 'resolved', 'alerts': [{'status': 'firing', 'labels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'annotations': {'description': 'MTU has been changed to 9000', 'title': 'MTU has been changed'}, 'startsAt': '2023-11-08T08:05:01.304Z', 'endsAt': '0001-01-01T00:00:00Z', 'generatorURL': 'http://85a4e3b559fe:9090/graph?g0.expr=node_network_mtu_bytes%7Bdevice%3D%22lo%22%7D+%3D%3D+9000&g0.tab=1', 'fingerprint': 'f56905cb7236a325'}], 'groupLabels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'commonLabels': {'alertname': 'mtu', 'device': 'lo', 'instance': 'hana01:9100', 'job': 'prometheus', 'monitor': 'GrafHana-monitor'}, 'commonAnnotations': {'description': 'MTU has been changed to 9000', 'title': 'MTU has been changed'}, 'externalURL': 'http://c287739b59a5:9093', 'version': '4', 'groupKey': '{}:{alertname="mtu", device="lo", instance="hana01:9100", job="prometheus", monitor="GrafHana-monitor"}', 'truncatedAlerts': 0}


r = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})


