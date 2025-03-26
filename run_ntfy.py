#!/usr/bin/env python3
import argparse
import sys
from ntfy_loop import NtfyLooper

def parse_arguments():
    """Parse command-line arguments for the run script."""
    parser = argparse.ArgumentParser(
        description="Run the NTFY message sender with default settings.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--iterations", "-n", type=int, default=5,
        help="Maximum number of messages to send. Default is 5."
    )
    parser.add_argument(
        "--interval", "-i", type=float, default=60.0,
        help="Time to wait between messages in seconds. Default is 60 seconds."
    )
    parser.add_argument(
        "--message", type=str, default="Test message from Replit run button",
        help="The message content to send."
    )
    parser.add_argument(
        "--title", type=str, default="Replit Alert",
        help="Title of the notification."
    )
    parser.add_argument(
        "--tags", type=str, default="warning,test",
        help="Comma-separated list of tags (e.g., 'warning,skull')."
    )
    parser.add_argument(
        "--topic", type=str, default="my_test",
        help="The ntfy.sh topic to send to."
    )
    parser.add_argument(
        "--priority", type=int, choices=range(1, 6), default=3,
        help="Priority level (1-5)."
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Display detailed output including response body."
    )
    
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Configuration from arguments
    topic = args.topic
    message = args.message
    title = args.title
    tags = args.tags
    priority = args.priority
    interval = args.interval
    iterations = args.iterations
    verbose = args.verbose
    
    print("╔══════════════════════════════════════════╗")
    print("║       NTFY.SH MESSAGE SENDER             ║")
    print("╚══════════════════════════════════════════╝")
    print(f"Topic:      {topic}")
    print(f"Message:    {message}")
    print(f"Title:      {title}")
    print(f"Tags:       {tags}")
    print(f"Priority:   {priority}")
    print(f"Interval:   {interval} seconds")
    print(f"Iterations: {iterations}")
    print("\nPress Ctrl+C to stop early\n")
    
    try:
        # Create and run the NtfyLooper with the specified settings
        looper = NtfyLooper(
            topic=topic,
            message=message,
            title=title,
            tags=tags,
            priority=priority,
            interval=interval,
            max_iterations=iterations,
            verbose=verbose
        )
        
        looper.run()
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()