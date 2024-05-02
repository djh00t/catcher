# catcher
Daemon that watches for specific shell responses which trigger configurable responses.

## Overview
The `catcher` daemon monitors terminal sessions for specific output patterns and executes predefined actions when these patterns are detected. This helps automate responses to common errors or notifications in a Unix-like environment.

## Installation
To install the daemon, follow these steps:
1. Ensure Python is installed on your system.
2. Clone the repository to your local machine.
3. Navigate to the repository directory and run:
   ```
   python daemon.py install
   ```
   This command adds the daemon to your shell profile so that it starts automatically when you open a terminal.

## Uninstallation
To uninstall the daemon, use the following command from the repository directory:
   ```
   python daemon.py uninstall
   ```
   This command removes the daemon from your shell profile.

## Configuration
The daemon's behavior is configured via a JSON file located at `~/.catcher/config.json`. This file contains patterns and actions in the following format:
   ```json
   {
       "errors": [
           {
               "pattern": "error message or pattern",
               "action": "command to execute"
           }
       ]
   }
   ```
   - **pattern**: A substring to look for in terminal output.
   - **action**: A command that will be executed in the terminal when the pattern is detected.

   To modify the daemon's behavior, edit this file and add your custom patterns and actions.

## Usage
Once installed, the daemon runs in the background of your terminal sessions. It continuously monitors for configured patterns and executes the associated actions when patterns are detected.

## Support
For issues, questions, or contributions, please refer to the repository's issues section or submit a pull request.
