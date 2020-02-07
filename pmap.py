#!/usr/bin/env python

import sys
import time
import platform
import datetime

import psutil
import influxdb


def main():
    if len(sys.argv) != 4:
        sys.exit('usage: pmap <pid> <influxdb-host> <influxdb-udp-port>')
    pid = int(sys.argv[1])
    process = psutil.Process(pid)
    influx = influxdb.InfluxDBClient(host=sys.argv[2], use_udp=True, udp_port=int(sys.argv[3]))
    host = platform.node()
    while True:
        maps = list(process.memory_maps(grouped=False))
        process_mmap = {
            "measurement": "process.mmap",
            "fields": {
                "host":                 host,
                "pid":                  pid,
                "count":                len(maps),
                "count_anon":           len([m for m in maps if m.path == '[anon]']),
                "total_rss":            sum(m.rss for m in maps),
                "total_private_dirty":  sum(m.private_dirty for m in maps),
            },
        }
        influx.write_points([process_mmap])
        time.sleep(0.5)


if __name__ == '__main__':
    main()
