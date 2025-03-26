# Ntfy.sh Message Loop

This Python script sends messages to [ntfy.sh](https://ntfy.sh) in a configurable loop. It's perfect for setting up periodic notifications or alerts.

## Quick Start with Replit

### Option 1: Interactive Mode (Recommended)
Just click the Run button or type:
```bash
python interactive_ntfy.py
```

This will:
- Prompt you for a notification title
- Ask for the message body
- Ask for the topic name (without the ntfy.sh/ prefix)
- Send a single notification after confirmation

### Option 2: Run from Shell with Pre-configured Settings
Open the Shell and type:
```bash
python run_ntfy.py
```

This will:
- Send 5 messages to ntfy.sh/efenow_alerts
- Use a 1-minute interval between messages
- Include a title, tags, and priority level

To customize these default settings, edit the variables in the `run_ntfy.py` file or use command-line arguments.

### Option 3: Create a Custom Workflow
1. Click on **Tools** in the sidebar
2. Select **Workflows** 
3. Click **Create workflow**
4. Name it "Run NTFY Script"
5. Add a shell command task with: `python interactive_ntfy.py`
6. Save the workflow
7. Now you can run it from the workflows panel or set it as the default run button action

### Option 4: Run with Custom Parameters
```bash
python ntfy_loop.py --message "Your message" --title "Your Title" --interval 30 --iterations 10
```

Or use the interactive mode with custom parameters:
```bash
python interactive_ntfy.py --tags "warning,skull" --priority 5
```

## Features

- Send messages to any ntfy.sh topic (defaults to `efenow_alerts`)
- Configure message title, tags, priority, and delivery delay
- Control the interval between messages
- Limit the total number of messages sent
- Graceful termination with Ctrl+C
- Detailed logging and statistics

## Requirements

- Python 3.6+
- curl installed on your system

## Usage

### Basic Usage

Send a basic message to the default topic (`efenow_alerts`):

```bash
python ntfy_loop.py --message "System is running normally"
```

### Customized Usage

Specify a different topic and add a title:

```bash
python ntfy_loop.py --topic "my_alerts" --message "CPU usage high" --title "Server Alert"
```

Add tags and set a high priority:

```bash
python ntfy_loop.py --message "Critical error detected" --tags "warning,skull" --priority 5
```

Set a custom interval (60 seconds) and limit the number of messages:

```bash
python ntfy_loop.py --message "Hourly check-in" --interval 60 --iterations 24
```

### All Available Options

```
usage: ntfy_loop.py [-h] [--topic TOPIC] --message MESSAGE [--title TITLE] [--tags TAGS]
                   [--priority {1,2,3,4,5}] [--delay DELAY] [-i INTERVAL] [-n ITERATIONS] [-v]
                   [--log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]

Send ntfy.sh messages in a loop with configurable parameters.

options:
  -h, --help            show this help message and exit
  --topic TOPIC         The ntfy.sh topic to send to. Default is 'efenow_alerts'. (default: efenow_alerts)
  --message MESSAGE     The message content to send. (default: None)
  --title TITLE         Title of the notification. (default: None)
  --tags TAGS           Comma-separated list of tags (e.g., 'warning,skull'). (default: None)
  --priority {1,2,3,4,5}
                        Priority level (1-5). (default: None)
  --delay DELAY         Delivery delay (e.g., '10m', '1h'). (default: None)
  -i INTERVAL, --interval INTERVAL
                        Time to wait between messages in seconds. (default: 300.0)
  -n ITERATIONS, --iterations ITERATIONS
                        Maximum number of messages to send. If not specified, the loop will run indefinitely. (default: None)
  -v, --verbose         Display detailed output including response body. (default: False)
  --log-level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set the logging level. (default: INFO)
```

## Examples

### Send a critical alert every 5 minutes for an hour

```bash
python ntfy_loop.py --message "Server temperature critical!" --title "Temperature Alert" --tags "warning,thermometer" --priority 5 --interval 300 --iterations 12
```

### Send a delayed notification

```bash
python ntfy_loop.py --message "Meeting starts in 30 minutes" --title "Meeting Reminder" --tags "calendar" --delay "30m"
```

### Run indefinitely with verbose output

```bash
python ntfy_loop.py --message "Heartbeat check" --title "System Monitor" --interval 3600 --verbose
```

## Ntfy.sh Documentation

For more information about ntfy.sh features and capabilities, visit [ntfy.sh documentation](https://docs.ntfy.sh/).

## License

This script is provided as-is under the MIT License.