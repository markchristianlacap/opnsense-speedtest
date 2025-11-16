#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
OPNsense Speedtest Plugin Script.

Copyright (C) 2021 M. Kralj
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import csv
import json
import os.path
import re
import statistics
import subprocess
import sys
from datetime import datetime
from os import path

# Constants
SPEEDTEST_BINARY = "speedtest"
CSV_FILE_PATH = "/usr/local/opnsense/scripts/OPNsense/speedtest/speedtest.csv"
CSV_FIELDS = [
    'Timestamp', 'ClientIp', 'ServerId', 'ServerName',
    'Country', 'DlSpeed', 'UlSpeed', 'Latency', 'Link'
]


def is_int(n):
    """Check if a value can be converted to an integer."""
    try:
        int(n)
        return True
    except ValueError:
        return False

#speedtest = "/usr/local/opnsense/scripts/OPNsense/speedtest/speedtest"
csvfile = CSV_FILE_PATH

arg = ''
if len(sys.argv) > 1:
    arg = str(sys.argv[1]) 

try:
    # If CSV doesn't exist, create one with headers
    if not path.isfile(csvfile):
        with open(csvfile, 'a', encoding="utf-8") as f:
            csv.writer(f, dialect='excel').writerow(CSV_FIELDS)

    # Parameter l or log - return the last 50 entries from csv
    if arg in ('l', 'log'):
        array = []
        with open(csvfile, 'r', encoding="utf-8") as f:
            data = csv.reader(f, dialect='excel')
            next(data)  # Skip header
            for row in data:
                # Convert timestamp to visual form
                row[0] = datetime.fromtimestamp(float(row[0])).isoformat()
                array.append(row)

        array = sorted(array, reverse=True)
        print(json.dumps(array[:50]))
        quit()

    # Parameter s or stat - return statistics
    if arg in ('s', 'stat'):
        latency_array = []
        download_array = []
        upload_array = []
        time_array = []
        with open(csvfile, 'r', encoding="utf-8") as f:
            data = csv.reader(f, dialect='excel')
            line = 0
            for row in data:
                if line > 0:
                    time_array.append(datetime.fromtimestamp(float(row[0])))
                    download_array.append(float(row[5]))
                    upload_array.append(float(row[6]))
                    latency_array.append(float(row[7]))
                line += 1
            line -= 1

        if line == 0:
            latency_array = [0]
            download_array = [0]
            upload_array = [0]
            time_array = [datetime.now()]

        out = {
            'samples': line,
            'period': {
                'oldest': str(min(time_array)),
                'youngest': str(max(time_array)),
            },
            'latency': {
                'avg': round(statistics.mean(latency_array), 2),
                'min': round(min(latency_array), 2),
                'max': round(max(latency_array), 2),
            },
            'download': {
                'avg': round(statistics.mean(download_array), 2),
                'min': round(min(download_array), 2),
                'max': round(max(download_array), 2),
            },
            'upload': {
                'avg': round(statistics.mean(upload_array), 2),
                'min': round(min(upload_array), 2),
                'max': round(max(upload_array), 2),
            }
        }
        print(json.dumps(out))
        quit()

    # Check the version of speedtest
    version = subprocess.run(
        [SPEEDTEST_BINARY, "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True
    ).stdout.decode('utf-8')
    bin_version = version.find("Ookla") > 0

    # Parameter v or version - return the version string
    if arg in ('v', 'version'):
        if bin_version:
            out = {"version": "binary", "message": version.splitlines()[0]}
        else:
            out = {"version": "cli", "message": f"{version.splitlines()[0]} {version.splitlines()[1]}"}
        print(json.dumps(out))
        quit()

    # Parameter t or list - return the list of servers available
    if arg in ('t', 'list'):
        array = []
        if bin_version:
            # Binary version: parse JSON output
            cmd = [SPEEDTEST_BINARY, '--accept-license', '--accept-gdpr', '--servers', '-fjsonl']
            serverlist = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True
            ).stdout.decode('utf-8').splitlines()
            for line in serverlist:
                tt = json.loads(line)
                out = {
                    'id': str(tt['id']),
                    'name': tt['name'],
                    'location': tt['location'],
                    'country': tt['country']
                }
                array.append(out)
        else:
            # CLI version: parse text output
            cmd = [SPEEDTEST_BINARY, '--list']
            serverlist = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=True
            ).stdout.decode('utf-8').splitlines()
            for line in serverlist[1:11]:
                rec = re.split(r"\) | \(|, ", line)
                out = {
                    'id': rec[0].strip(),
                    "name": rec[1].strip(),
                    "location": f"{rec[2].strip()}, {rec[3]}",
                    "country": rec[4].strip()
                }
                array.append(out)
        print(json.dumps(array))
        quit()

    # Run speedtest with no arguments or with '0' - let speedtest decide server
    elif arg == '' or arg == '0':
        if bin_version:
            cmd = [SPEEDTEST_BINARY, '--accept-license', '--accept-gdpr', '-fjson']
        else:
            cmd = [SPEEDTEST_BINARY, '--json', '--share']
    # Run speedtest with integer: supply the argument as server ID
    elif is_int(arg):
        if bin_version:
            cmd = [SPEEDTEST_BINARY, '--accept-license', '--accept-gdpr', '-fjson', f'-s{arg}']
        else:
            cmd = [SPEEDTEST_BINARY, '--json', '--share', '--server', arg]
    else:
        # Invalid argument
        out = {'error': f'{arg} is invalid server id'}
        print(json.dumps(out))
        quit()

    # Run the speedtest command
    result = json.loads(subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True
    ).stdout.decode('utf-8'))

    # Assemble output JSON to be consistent regardless of source
    out = {}
    if bin_version:
        out['timestamp'] = result['timestamp']
        out['clientip'] = result['interface']['externalIp']
        out['serverid'] = result['server']['id']
        out['servername'] = f"{result['server']['name']}, {result['server']['location']}"
        out['country'] = result['server']['country']
        out['latency'] = round(result['ping']['latency'], 2)
        out['download'] = round(result['download']['bandwidth'] / 125000, 2)
        out['upload'] = round(result['upload']['bandwidth'] / 125000, 2)
        out['link'] = result['result']['url']
    else:
        out['timestamp'] = result['timestamp'][:-8] + 'Z'
        out['clientip'] = result['client']['ip']
        out['serverid'] = result['server']['id']
        out['servername'] = f"{result['server']['sponsor']}, {result['server']['name']}"
        out['country'] = result['server']['country']
        out['latency'] = round(result['ping'], 2)
        out['download'] = round(result['download'] / 1000000, 2)
        out['upload'] = round(result['upload'] / 1000000, 2)
        out['link'] = result['share'][:-4]

    # Store result in CSV (datetime in CSV uses different format)
    csvtime = datetime.strptime(out['timestamp'], "%Y-%m-%dT%H:%M:%SZ").timestamp()
    newrow = [
        csvtime, out['clientip'], out['serverid'], out['servername'],
        out['country'], out['download'], out['upload'], out['latency'], out['link']
    ]

    with open(csvfile, 'a', encoding="utf-8") as f:
        writer = csv.writer(f, dialect='excel')
        writer.writerow(newrow)

    # Return the assembled JSON for further processing
    print(json.dumps(out), file=sys.stdout)

except (OSError, IOError):
    out = {'version': 'none', 'message': 'No speedtest package installed'}
    print(json.dumps(out))
except subprocess.CalledProcessError:
    out = {'error': f'Speedtest server id {arg} not recognized.'}
    print(json.dumps(out))