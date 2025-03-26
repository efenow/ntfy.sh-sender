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

class CurlLooper:
    """A class to execute a curl command in a loop with configurable parameters."""
    
    def __init__(self, 
                 curl_command: List[str], 
                 interval: float = 1.0, 
                 max_iterations: Optional[int] = None,
                 timeout: Optional[float] = None,
                 success_only: bool = False,
                 verbose: bool = False):
        """
        Initialize the CurlLooper with the specified parameters.
        
        Args:
            curl_command: The curl command to execute as a list of strings.
            interval: Time to wait between requests in seconds.
            max_iterations: Maximum number of iterations, or None for infinite.
            timeout: Timeout for each curl command in seconds, or None for no timeout.
            success_only: If True, only log successful requests.
            verbose: If True, display detailed output including response body.
        """
        self.curl_command = curl_command
        self.interval = interval
        self.max_iterations = max_iterations
        self.timeout = timeout
        self.success_only = success_only
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
        
    def execute_curl(self) -> Union[subprocess.CompletedProcess, subprocess.CalledProcessError]:
        """
        Execute the curl command and return the result.
        
        Returns:
            The completed process or called process error.
        """
        try:
            # Execute the curl command
            process = subprocess.run(
                self.curl_command,
                capture_output=True,
                text=True,
                check=True,
                timeout=self.timeout
            )
            return process
        except subprocess.CalledProcessError as e:
            return e
        except subprocess.TimeoutExpired:
            logger.error(f"Curl command timed out after {self.timeout} seconds")
            return subprocess.CompletedProcess(
                args=self.curl_command,
                returncode=-1,
                stdout="",
                stderr=f"Timed out after {self.timeout} seconds"
            )
        except Exception as e:
            logger.error(f"Error executing curl command: {str(e)}")
            return subprocess.CompletedProcess(
                args=self.curl_command,
                returncode=-1,
                stdout="",
                stderr=str(e)
            )
            
    def log_result(self, result):
        """
        Log the result of a curl execution.
        
        Args:
            result: The subprocess.CompletedProcess or subprocess.CalledProcessError.
        """
        if result.returncode == 0:
            self.success_count += 1
            if not self.success_only or self.verbose:
                logger.info(f"Iteration {self.iteration_count}: Success")
                if self.verbose:
                    logger.info(f"Response: {result.stdout.strip()}")
        else:
            self.failure_count += 1
            logger.error(f"Iteration {self.iteration_count}: Failed with code {result.returncode}")
            logger.error(f"Error: {result.stderr.strip()}")
            if self.verbose and hasattr(result, 'stdout') and result.stdout:
                logger.info(f"Response: {result.stdout.strip()}")
                
    def run(self):
        """Run the curl command in a loop according to the configuration."""
        logger.info(f"Starting curl loop with command: {' '.join(self.curl_command)}")
        logger.info(f"Interval: {self.interval} seconds")
        if self.max_iterations:
            logger.info(f"Maximum iterations: {self.max_iterations}")
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
                
                # Execute the curl command and log the result
                result = self.execute_curl()
                self.log_result(result)
                
                # Wait for the specified interval before the next iteration
                if self.running and (self.max_iterations is None or self.iteration_count < self.max_iterations):
                    time.sleep(self.interval)
                    
        finally:
            # Print summary statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("\nExecution Summary:")
            logger.info(f"Total iterations: {self.iteration_count}")
            logger.info(f"Successful requests: {self.success_count}")
            logger.info(f"Failed requests: {self.failure_count}")
            logger.info(f"Total execution time: {duration:.2f} seconds")
            if self.iteration_count > 0:
                logger.info(f"Average request time: {duration / self.iteration_count:.2f} seconds")
                logger.info(f"Success rate: {self.success_count / self.iteration_count * 100:.2f}%")

def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Execute a curl command in a loop with configurable parameters.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "curl_command",
        nargs="+",
        help="The curl command to execute (without the 'curl' part). All arguments will be passed to curl."
    )
    
    parser.add_argument(
        "-i", "--interval",
        type=float,
        default=1.0,
        help="Time to wait between requests in seconds."
    )
    
    parser.add_argument(
        "-n", "--iterations",
        type=int,
        help="Maximum number of iterations. If not specified, the loop will run indefinitely."
    )
    
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        help="Timeout for each curl command in seconds."
    )
    
    parser.add_argument(
        "-s", "--success-only",
        action="store_true",
        help="Only log successful requests."
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
    
    # Prepend 'curl' to the command
    curl_command = ["curl"] + args.curl_command
    
    # Create and run the CurlLooper
    looper = CurlLooper(
        curl_command=curl_command,
        interval=args.interval,
        max_iterations=args.iterations,
        timeout=args.timeout,
        success_only=args.success_only,
        verbose=args.verbose
    )
    
    looper.run()

if __name__ == "__main__":
    main()
