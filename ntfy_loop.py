#!/usr/bin/env python3

import argparse
import logging
import signal
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional, List, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def send_ntfy_message(topic, message, title=None, tags=None, priority=None, delay=None):
    """
    Send a message to ntfy.sh
    
    Args:
        topic (str): The ntfy topic to send to
        message (str): The message to send
        title (str, optional): Title of the notification
        tags (str, optional): Comma-separated list of tags (e.g., "warning,skull")
        priority (int, optional): Priority level (1-5)
        delay (str, optional): Delivery delay (e.g., "10m", "1h")
    
    Returns:
        subprocess.CompletedProcess: The result of the curl command
    """
    curl_command = ["curl", "-s", f"https://ntfy.sh/{topic}"]
    
    # Add optional headers
    if title:
        curl_command.extend(["-H", f"Title: {title}"])
    if tags:
        curl_command.extend(["-H", f"Tags: {tags}"])
    if priority:
        curl_command.extend(["-H", f"Priority: {priority}"])
    if delay:
        curl_command.extend(["-H", f"Delay: {delay}"])
    
    # Add the message as data
    curl_command.extend(["-d", message])
    
    try:
        process = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True
        )
        return process
    except subprocess.CalledProcessError as e:
        logger.error(f"Error sending message: {e}")
        return e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return subprocess.CompletedProcess(
            args=curl_command,
            returncode=-1,
            stdout="",
            stderr=str(e)
        )

class NtfyLooper:
    """A class to send ntfy.sh messages in a loop with configurable parameters."""
    
    def __init__(self, 
                 topic: str,
                 message: str,
                 title: Optional[str] = None,
                 tags: Optional[str] = None,
                 priority: Optional[int] = None,
                 delay: Optional[str] = None,
                 interval: float = 300.0,
                 max_iterations: Optional[int] = None,
                 verbose: bool = False):
        """
        Initialize the NtfyLooper with the specified parameters.
        
        Args:
            topic: The ntfy.sh topic to send to.
            message: The message content to send.
            title: Optional title for the notification.
            tags: Optional comma-separated tags for the notification.
            priority: Optional priority level (1-5).
            delay: Optional delivery delay (e.g., "10m").
            interval: Time to wait between messages in seconds.
            max_iterations: Maximum number of messages to send, or None for infinite.
            verbose: If True, display detailed output.
        """
        self.topic = topic
        self.message = message
        self.title = title
        self.tags = tags
        self.priority = priority
        self.delay = delay
        self.interval = interval
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.iteration_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.running = True
        
        # Set up signal handling for graceful termination
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)
        
    def _handle_signal(self, signum, frame):
        """Handle termination signals by setting running flag to False."""
        logger.info(f"Received signal {signum}, stopping after current iteration...")
        self.running = False
    
    def log_result(self, result):
        """
        Log the result of a message send.
        
        Args:
            result: The subprocess.CompletedProcess or subprocess.CalledProcessError.
        """
        if result.returncode == 0:
            self.success_count += 1
            logger.info(f"Message {self.iteration_count}: Successfully sent to ntfy.sh/{self.topic}")
            if self.verbose:
                logger.info(f"Response: {result.stdout.strip()}")
        else:
            self.failure_count += 1
            logger.error(f"Message {self.iteration_count}: Failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr.strip()}")
            if self.verbose and hasattr(result, 'stdout') and result.stdout:
                logger.info(f"Response: {result.stdout.strip()}")
    
    def run(self):
        """Run the ntfy sender in a loop according to the configuration."""
        logger.info(f"Starting ntfy loop to topic: {self.topic}")
        logger.info(f"Message: {self.message}")
        if self.title:
            logger.info(f"Title: {self.title}")
        if self.tags:
            logger.info(f"Tags: {self.tags}")
        if self.priority:
            logger.info(f"Priority: {self.priority}")
        if self.delay:
            logger.info(f"Delay: {self.delay}")
        logger.info(f"Interval: {self.interval} seconds")
        
        if self.max_iterations:
            logger.info(f"Maximum messages: {self.max_iterations}")
        else:
            logger.info("Running indefinitely. Press Ctrl+C to stop.")
        
        start_time = datetime.now()
        
        try:
            while self.running:
                self.iteration_count += 1
                
                # Check if we've reached the maximum number of iterations
                if self.max_iterations and self.iteration_count > self.max_iterations:
                    logger.info(f"Reached maximum iterations ({self.max_iterations}), stopping.")
                    break
                
                # Send the ntfy message and log the result
                result = send_ntfy_message(
                    self.topic,
                    self.message,
                    self.title,
                    self.tags,
                    self.priority,
                    self.delay
                )
                
                self.log_result(result)
                
                # Wait for the specified interval before the next iteration
                if self.running and (self.max_iterations is None or self.iteration_count < self.max_iterations):
                    time.sleep(self.interval)
                    
        finally:
            # Print summary statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("\nExecution Summary:")
            logger.info(f"Total messages sent: {self.iteration_count}")
            logger.info(f"Successful messages: {self.success_count}")
            logger.info(f"Failed messages: {self.failure_count}")
            logger.info(f"Total execution time: {duration:.2f} seconds")
            if self.iteration_count > 0:
                logger.info(f"Success rate: {self.success_count / self.iteration_count * 100:.2f}%")

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Send ntfy.sh messages in a loop with configurable parameters.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--topic",
        default="efenow_alerts",
        help="The ntfy.sh topic to send to. Default is 'efenow_alerts'."
    )
    
    parser.add_argument(
        "--message",
        required=True,
        help="The message content to send."
    )
    
    parser.add_argument(
        "--title",
        help="Title of the notification."
    )
    
    parser.add_argument(
        "--tags",
        help="Comma-separated list of tags (e.g., 'warning,skull')."
    )
    
    parser.add_argument(
        "--priority",
        type=int,
        choices=range(1, 6),
        help="Priority level (1-5)."
    )
    
    parser.add_argument(
        "--delay",
        help="Delivery delay (e.g., '10m', '1h')."
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=300.0,
        help="Time to wait between messages in seconds."
    )
    
    parser.add_argument(
        "-n", "--iterations",
        type=int,
        help="Maximum number of messages to send. If not specified, the loop will run indefinitely."
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display detailed output including response body."
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level."
    )
    
    return parser.parse_args()

def main():
    """Main entry point of the script."""
    args = parse_arguments()
    
    # Set log level based on command-line argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create and run the NtfyLooper
    looper = NtfyLooper(
        topic=args.topic,
        message=args.message,
        title=args.title,
        tags=args.tags,
        priority=args.priority,
        delay=args.delay,
        interval=args.interval,
        max_iterations=args.iterations,
        verbose=args.verbose
    )
    
    looper.run()

if __name__ == "__main__":
    main()