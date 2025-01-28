from flask import Flask, render_template, jsonify
import psutil
import platform
import socket
import netifaces
from ping3 import ping
import json
from datetime import datetime

app = Flask(__name__)

def get_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.percent,
        'hostname': socket.gethostname(),
        'platform': platform.platform(),
        'python_version': platform.python_version()
    }

def get_network_info():
    interfaces = []
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:
            for addr in addrs[netifaces.AF_INET]:
                interfaces.append({
                    'interface': iface,
                    'ip': addr['addr'],
                    'netmask': addr['netmask']
                })
    return interfaces

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system')
def system():
    return jsonify(get_system_info())

@app.route('/api/network')
def network():
    return jsonify(get_network_info())

@app.route('/api/ping/<host>')
def ping_host(host):
    try:
        response_time = ping(host)
        if response_time is None:
            return jsonify({'status': 'failed', 'message': 'Host unreachable'})
        return jsonify({'status': 'success', 'response_time': round(response_time * 1000, 2)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
