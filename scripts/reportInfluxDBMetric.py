from datetime import datetime, timedelta
import socket
from influxdb import InfluxDBClient
from pyhocon import ConfigFactory
import sys

def reportInfluxDBMetric(metric, value, host, port):
    json_body = {
        "tags": {
            "host": socket.gethostname()
        },
        "time": (datetime.now()-timedelta(seconds=value)).isoformat(),
        "points": [{
            "measurement": metric,
            "fields": {
                "value": value
            }
        }]
    }
    client = InfluxDBClient(host=host, use_udp=True, udp_port=port)
    client.send_packet(json_body)

if __name__ == '__main__':
    metric = str(sys.argv[1])
    value = float(sys.argv[2])
    config_path = str(sys.argv[3])

    conf = ConfigFactory.parse_file(config_path)
    influx_host = conf['influx_host']
    influx_port = conf['influx_port']

    #influx use different ports to distinguish between databases when using UDP,
    #so we do not specify database
    reportInfluxDBMetric(metric, value, influx_host, influx_port)
