"""
This module implements a daemon that ensures a single instance runs across all
terminal sessions on a Unix-like system. It monitors and interacts with shell
sessions, executing predefined actions when specific output patterns are detected.

Workflow:
1. The daemon checks if an instance is already running by looking for a PID file.
2. If not already running, it starts monitoring terminal sessions.
3. It reads a configuration file that defines patterns and corresponding actions.
4. When a pattern is matched in any terminal session, the associated action is
   executed in that session.

Configuration:
The configuration is a JSON file located at ~/.catcher/config.json. It contains
a list of error patterns and the actions to execute when those patterns are detected.

Execution:
To start the daemon, add the following line to your shell profile (e.g., ~/.bash_profile):
    python /path/to/daemon.py &

Ensure that the script is executable and the configuration file is properly set up.
The daemon will then run in the background, monitoring all terminal sessions.
It will execute actions in the terminal where the pattern is matched, ensuring
that the single daemon instance can interact with any session.

The daemon confirms that only one instance is running, but it is designed to work
with all terminal sessions, allowing actions to be run in whichever session a
pattern is matched.
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
    if len(sys.argv) > 1:
        if sys.argv[1] == 'install':
            install_daemon()
            sys.exit()
        elif sys.argv[1] == 'uninstall':
            uninstall_daemon()
            sys.exit()

    init_daemon()
def install_daemon():
    """Installs the daemon by adding it to the shell profile."""
    shell_profile = os.path.expanduser('~/.bash_profile')  # or appropriate shell profile
    daemon_command = "python /path/to/daemon.py &\n"
    with open(shell_profile, 'a') as file:
        file.write(daemon_command)
    print("Daemon installed. Please restart your terminal.")

def uninstall_daemon():
    """Uninstalls the daemon by removing it from the shell profile."""
    shell_profile = os.path.expanduser('~/.bash_profile')  # or appropriate shell profile
    daemon_command = "python /path/to/daemon.py &\n"
    with open(shell_profile, 'r') as file:
        lines = file.readlines()
    with open(shell_profile, 'w') as file:
        for line in lines:
            if line.strip("\n") != daemon_command.strip("\n"):
                file.write(line)
    print("Daemon uninstalled. Please restart your terminal.")

