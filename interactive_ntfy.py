#!/usr/bin/env python3
"""
Interactive NTFY Message Sender
This script prompts the user for a title, message, and topic, then sends a notification.
"""

import sys
import argparse
from ntfy_loop import NtfyLooper, send_ntfy_message

def get_user_input(prompt, default=None):
    """Get input from user with an optional default value."""
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input if user_input.strip() else default
    else:
        return input(f"{prompt}: ")

def main():
    """Interactive main function that prompts for inputs."""
    parser = argparse.ArgumentParser(
        description="Interactive NTFY message sender.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--iterations", "-n", type=int, default=1,
        help="Number of messages to send (defaults to 1)."
    )
    parser.add_argument(
        "--interval", "-i", type=float, default=60.0,
        help="Time between messages in seconds (for multiple messages)."
    )
    parser.add_argument(
        "--tags", type=str, default="info",
        help="Comma-separated list of tags (e.g., 'warning,skull')."
    )
    parser.add_argument(
        "--priority", type=int, choices=range(1, 6), default=3,
        help="Priority level (1-5)."
    )
    
    args = parser.parse_args()
    
    # Display header
    print("╔══════════════════════════════════════════╗")
    print("║       NTFY.SH MESSAGE SENDER             ║")
    print("╚══════════════════════════════════════════╝")
    
    # Get user inputs
    title = get_user_input("Enter notification title", "Alert")
    message = get_user_input("Enter message body", "Notification from Replit")
    topic = get_user_input("Enter topic (without ntfy.sh/)", "my_test")
    
    # Display configuration
    print("\n--- Configuration ---")
    print(f"Topic:      ntfy.sh/{topic}")
    print(f"Message:    {message}")
    print(f"Title:      {title}")
    print(f"Tags:       {args.tags}")
    print(f"Priority:   {args.priority}")
    
    if args.iterations > 1:
        print(f"Interval:   {args.interval} seconds")
        print(f"Iterations: {args.iterations}")
        
        # Confirm before sending multiple messages
        confirm = input("\nSend multiple messages? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            sys.exit(0)
            
        # Create and run the NtfyLooper
        try:
            looper = NtfyLooper(
                topic=topic,
                message=message,
                title=title,
                tags=args.tags,
                priority=args.priority,
                interval=args.interval,
                max_iterations=args.iterations,
                verbose=True
            )
            
            print("\nPress Ctrl+C to stop early\n")
            looper.run()
            
        except KeyboardInterrupt:
            print("\nStopped by user")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
            
    else:
        # Confirm before sending a single message
        confirm = input("\nSend this message? (y/n): ").lower()
        if confirm != 'y':
            print("Operation cancelled.")
            sys.exit(0)
            
        # Send a single message
        try:
            print("\nSending message...")
            result = send_ntfy_message(
                topic=topic,
                message=message,
                title=title,
                tags=args.tags,
                priority=args.priority
            )
            print(f"Message sent successfully to ntfy.sh/{topic}")
            
        except Exception as e:
            print(f"Error sending message: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()