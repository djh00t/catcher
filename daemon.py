"""
This module ensures that only a single instance of the daemon runs across all
terminal sessions. It monitors and interacts with bash sessions, reacting to
specific outputs based on defined patterns in a configuration file.

Usage:
    Add to ~/.bash_profile:
        python /path/to/script.py &

This script checks if it is already running in another terminal and exits if so,
ensuring only one daemon manages all sessions.
"""

import subprocess
import os
import sys
import json
from threading import Thread
from queue import Queue

def monitor_terminal(queue):
    """ Monitors terminal input and output, executing actions based on config. """
    config = load_config()
    config_path = os.path.expanduser('~/.catcher/config.json')
    last_modified = os.path.getmtime(config_path)
    
    while True:
        line = queue.get()
        if line is None:
            break  # End monitoring if None is received.
        
        new_config, last_modified = check_config_update(last_modified, config_path)
        if new_config:
            config = new_config
        
        for error in config['errors']:
            if error['pattern'] in line:
                print(f"Detected error: {error['pattern']}. Executing...")
                execute_in_terminal(error['action'])

def execute_in_terminal(command):
    """ Executes a command in the current terminal session. """
    os.system(command)

def load_config():
    """ Loads configuration from JSON file located in the ~/.catcher directory. """
    config_path = os.path.expanduser('~/.catcher/config.json')
    with open(config_path, 'r') as file:
        return json.load(file)

def check_config_update(last_modified, config_path):
    """ Reloads configurations if the config file has been updated. """
    current_modified = os.path.getmtime(config_path)
    if current_modified != last_modified:
        print("Config updated, reloading...")
        return load_config(), current_modified
    return None, last_modified

def daemon_already_running():
    """ Checks if the daemon is already running using a PID file. """
    pid_file = os.path.expanduser('~/.catcher/daemon.pid')
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as file:
            pid = int(file.read().strip())
            # Check if process is really running
            if os.path.exists(f'/proc/{pid}'):
                return True
    # Write current PID
    with open(pid_file, 'w') as file:
        file.write(str(os.getpid()))
    return False

def init_daemon():
    """ Initializes the daemon, ensuring only one instance runs. """
    if daemon_already_running():
        print("Daemon already running.")
        return

    queue = Queue()
    monitor_thread = Thread(target=monitor_terminal, args=(queue,))
    monitor_thread.start()

    try:
        while True:
            line = sys.stdin.readline()
            queue.put(line)
    except KeyboardInterrupt:
        queue.put(None)  # Signal the monitoring thread to end.
        monitor_thread.join()

if __name__ == "__main__":
    init_daemon()
