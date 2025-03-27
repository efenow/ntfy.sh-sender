#!/usr/bin/env python3
"""
Dual-purpose main module:
1. Provides a Flask web app for gunicorn (Start application workflow)
2. Can be run directly to launch the interactive NTFY sender
"""

import os
import sys
import subprocess
try:
    from flask import Flask, render_template_string, redirect, url_for, request
except ImportError:
    # In case Flask is not available (likely during debugging)
    Flask = None
    render_template_string = None
    redirect = None
    url_for = None
    request = None
import threading
import webbrowser

# Create Flask app
app = Flask(__name__)

# HTML template for the NTFY interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>efenow's NTFY.SH Sender</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 2rem;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .main-content {
            flex: 1;
        }
        .header-box {
            background-color: #212529;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .form-container {
            max-width: 700px;
            margin: 0 auto;
        }
        .card {
            margin-bottom: 1rem;
            background-color: #2d3338;
            border: 1px solid #343a40;
        }
        footer {
            margin-top: 3rem;
            padding: 2rem 0;
            background-color: #212529;
        }
    </style>
</head>
<body data-bs-theme="dark">
    <div class="container main-content">
        <div class="header-box">
            <h1> efenow's NTFY.sh Message Sender</h1>
            <p class="lead">Send notifications to any NTFY.sh topic</p>
        </div>
        
        <div class="form-container">
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Interactive Mode (Recommended)</h4>
                </div>
                <div class="card-body">
                    <p>Use our interactive shell script to send messages with guided prompts:</p>
                    <a href="/run-interactive" class="btn btn-primary">Run Interactive Script</a>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Run Demo Script</h4>
                </div>
                <div class="card-body">
                    <p>Try our pre-configured demo script:</p>
                    <form action="/run-ntfy-test" method="get" class="row g-3">
                        <div class="col-md-8">
                            <div class="input-group">
                                <span class="input-group-text">Topic</span>
                                <input type="text" class="form-control" name="topic" placeholder="Enter topic name" value="my_test">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <button type="submit" class="btn btn-outline-info w-100">Run efenow's NTFY Test</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="card mb-4">
                <div class="card-header">
                    <h4>Interactive NTFY Loop</h4>
                </div>
                <div class="card-body">
                    <p>Set up a repeated notification loop with custom parameters:</p>
                    <form action="/run-ntfy-loop" method="post" class="row g-3">
                        <div class="col-md-6">
                            <label for="loop-topic" class="form-label">Topic</label>
                            <input type="text" class="form-control" id="loop-topic" name="topic" value="my_test" required>
                        </div>
                        <div class="col-md-6">
                            <label for="loop-title" class="form-label">Title</label>
                            <input type="text" class="form-control" id="loop-title" name="title" value="Loop Alert" required>
                        </div>
                        <div class="col-12">
                            <label for="loop-message" class="form-label">Message</label>
                            <input type="text" class="form-control" id="loop-message" name="message" value="Periodic notification from Replit" required>
                        </div>
                        <div class="col-md-4">
                            <label for="loop-tags" class="form-label">Tags (comma-separated)</label>
                            <input type="text" class="form-control" id="loop-tags" name="tags" value="repeat,clock">
                        </div>
                        <div class="col-md-4">
                            <label for="loop-priority" class="form-label">Priority (1-5)</label>
                            <select class="form-select" id="loop-priority" name="priority">
                                <option value="1">1 - Min</option>
                                <option value="2">2 - Low</option>
                                <option value="3" selected>3 - Default</option>
                                <option value="4">4 - High</option>
                                <option value="5">5 - Max</option>
                            </select>
                        </div>
                        <div class="col-md-4">
                            <label for="loop-interval" class="form-label">Interval (seconds)</label>
                            <input type="number" class="form-control" id="loop-interval" name="interval" value="30" min="5" required>
                        </div>
                        <div class="col-md-4">
                            <label for="loop-iterations" class="form-label">Number of Messages</label>
                            <input type="number" class="form-control" id="loop-iterations" name="iterations" value="5" min="1" max="20" required>
                        </div>
                        <div class="col-12 mt-3">
                            <button type="submit" class="btn btn-primary">Start NTFY Loop</button>
                        </div>
                    </form>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <h4>Documentation</h4>
                </div>
                <div class="card-body">
                    <p>For detailed instructions and examples, view our documentation:</p>
                    <a href="https://github.com/yourusername/ntfy-message-loop" class="btn btn-success">View Documentation</a>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <div class="container">
            <div class="row">
                <div class="col-md-6">
                    <h5>About efenow's NTFY.sh Sender</h5>
                    <p>efenow's NTFY.sh Sender is a customized tool that lets you send notifications to your phone or desktop using the NTFY.sh service.</p>
                </div>
                <div class="col-md-6">
                    <h5>Related Links</h5>
                    <ul class="list-unstyled">
                        <li><a href="https://ntfy.sh" class="text-decoration-none">NTFY.sh Website</a></li>
                        <li><a href="https://docs.ntfy.sh" class="text-decoration-none">NTFY.sh Documentation</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main interface page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/run-interactive')
def run_interactive():
    """Run the interactive script and return results"""
    try:
        # Get the full path to interactive_ntfy.py
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive_ntfy.py")
        
        # Create a unique pipe-based input to simulate interactive input
        # We're providing default values that will be displayed in the web UI
        process = subprocess.Popen(
            [sys.executable, script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Capture just the initial output without sending input
        initial_output, _ = process.communicate(input="", timeout=1)
        process.terminate()
        
        # Return a page with the prompt and a form
        form_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NTFY.sh Interactive Sender</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding-top: 2rem;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                .main-content {{
                    flex: 1;
                }}
                .header-box {{
                    background-color: #212529;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 2rem;
                    text-align: center;
                }}
                .form-container {{
                    max-width: 700px;
                    margin: 0 auto;
                }}
                .card {{
                    margin-bottom: 1rem;
                    background-color: #2d3338;
                    border: 1px solid #343a40;
                }}
                footer {{
                    margin-top: 3rem;
                    padding: 2rem 0;
                    background-color: #212529;
                }}
                .terminal {{
                    background-color: #000;
                    color: #0f0;
                    font-family: monospace;
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container main-content">
                <div class="header-box">
                    <h1>efenow's NTFY.sh Interactive Sender</h1>
                    <p class="lead">Fill in the form to send a notification</p>
                </div>
                
                <div class="form-container">
                    <div class="card mb-4">
                        <div class="card-header">
                            <h4>Send Notification</h4>
                        </div>
                        <div class="card-body">
                            <form action="/send-notification" method="post">
                                <div class="mb-3">
                                    <label for="title" class="form-label">Notification Title</label>
                                    <input type="text" class="form-control" id="title" name="title" value="Alert" required>
                                </div>
                                <div class="mb-3">
                                    <label for="message" class="form-label">Message Body</label>
                                    <textarea class="form-control" id="message" name="message" rows="3" required>Notification from Replit</textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="topic" class="form-label">Topic (without ntfy.sh/)</label>
                                    <input type="text" class="form-control" id="topic" name="topic" value="my_test" required>
                                </div>
                                <div class="mb-3">
                                    <label for="tags" class="form-label">Tags (comma-separated)</label>
                                    <input type="text" class="form-control" id="tags" name="tags" value="info">
                                </div>
                                <div class="mb-3">
                                    <label for="priority" class="form-label">Priority (1-5)</label>
                                    <select class="form-select" id="priority" name="priority">
                                        <option value="1">1 - Min</option>
                                        <option value="2">2 - Low</option>
                                        <option value="3" selected>3 - Default</option>
                                        <option value="4">4 - High</option>
                                        <option value="5">5 - Max</option>
                                    </select>
                                </div>
                                <button type="submit" class="btn btn-primary">Send Notification</button>
                                <a href="/" class="btn btn-secondary ms-2">Back to Home</a>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer>
                <div class="container">
                    <div class="row">
                        <div class="col-md-6">
                            <h5>About efenow's NTFY.sh Sender</h5>
                            <p>efenow's NTFY.sh Sender is a customized tool that lets you send notifications to your phone or desktop using the NTFY.sh service.</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Related Links</h5>
                            <ul class="list-unstyled">
                                <li><a href="https://ntfy.sh" class="text-decoration-none">NTFY.sh Website</a></li>
                                <li><a href="https://docs.ntfy.sh" class="text-decoration-none">NTFY.sh Documentation</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </footer>
        </body>
        </html>
        """
        return form_html
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/send-notification', methods=['POST'])
def send_notification():
    """Process the notification form and send using the ntfy_loop.py script"""
    
    try:
        # Get form data
        title = request.form.get('title', 'Alert')
        message = request.form.get('message', 'Notification from Replit')
        topic = request.form.get('topic', 'my_test')
        tags = request.form.get('tags', 'info')
        priority = request.form.get('priority', '3')
        
        # Build command with proper arguments
        cmd = [
            sys.executable, 
            "ntfy_loop.py", 
            "--topic", topic,
            "--message", message,
            "--title", title
        ]
        
        if tags:
            cmd.extend(["--tags", tags])
        
        if priority:
            cmd.extend(["--priority", priority])
            
        # Add iterations to send just one message
        cmd.extend(["--iterations", "1"])
        
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return success page with output
        success_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Notification Sent</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding-top: 2rem;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                .main-content {{
                    flex: 1;
                }}
                .terminal {{
                    background-color: #1e1e1e;
                    color: #0f0;
                    font-family: monospace;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    max-height: 300px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container main-content">
                <div class="alert alert-success mt-4" role="alert">
                    <h4 class="alert-heading">Success!</h4>
                    <p>Your notification was sent to ntfy.sh/{topic}</p>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <h5>Notification Details</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item"><strong>Topic:</strong> ntfy.sh/{topic}</li>
                            <li class="list-group-item"><strong>Title:</strong> {title}</li>
                            <li class="list-group-item"><strong>Message:</strong> {message}</li>
                            <li class="list-group-item"><strong>Tags:</strong> {tags}</li>
                            <li class="list-group-item"><strong>Priority:</strong> {priority}</li>
                        </ul>
                    </div>
                </div>
                
                <h5 class="mt-4">Command Output:</h5>
                <div class="terminal">
{result.stdout}
                </div>
                
                <div class="mt-4">
                    <a href="/run-interactive" class="btn btn-primary">Send Another</a>
                    <a href="/" class="btn btn-secondary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return success_html
        
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}\n\nStdout:\n{e.stdout}\n\nStderr:\n{e.stderr}"
        return f"Error: {error_message}", 500
    except Exception as e:
        return f"Error: {str(e)}", 500
    
@app.route('/run-ntfy-test')
def run_ntfy_test():
    """Run the ntfy test workflow and display the results"""
    try:
        # Get the topic from the query parameter or use default
        topic = request.args.get('topic', 'my_test')
        
        # Execute the ntfy test command
        result = subprocess.run(
            [
                sys.executable, 
                "ntfy_loop.py", 
                "--topic", topic,
                "--message", "Test message from Replit", 
                "--title", "efenow's Test Alert", 
                "--tags", "warning,test", 
                "--interval", "2", 
                "--iterations", "1", 
                "--verbose"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Format the output in a nice HTML page
        output_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NTFY Test Results</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding-top: 2rem;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                .main-content {{
                    flex: 1;
                }}
                .terminal {{
                    background-color: #1e1e1e;
                    color: #0f0;
                    font-family: monospace;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container main-content">
                <h1 class="my-4">NTFY Test Results</h1>
                
                <div class="alert alert-success" role="alert">
                    <h4 class="alert-heading">Success!</h4>
                    <p>The NTFY test was executed successfully to ntfy.sh/{topic}</p>
                </div>
                
                <h5>Command Output:</h5>
                <div class="terminal">
{result.stdout}
                </div>
                
                <div class="mt-4 mb-5">
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return output_html
    except Exception as e:
        return f"Error running NTFY test: {str(e)}", 500

@app.route('/run-ntfy-loop', methods=['POST'])
def run_ntfy_loop():
    """Process the notification loop form and send recurring notifications"""
    
    try:
        # Get form data
        title = request.form.get('title', 'Loop Alert')
        message = request.form.get('message', 'Periodic notification from Replit')
        topic = request.form.get('topic', 'my_test')
        tags = request.form.get('tags', 'repeat,clock')
        priority = request.form.get('priority', '3')
        interval = request.form.get('interval', '30')
        iterations = request.form.get('iterations', '5')
        
        # Build command with proper arguments
        cmd = [
            sys.executable, 
            "ntfy_loop.py", 
            "--topic", topic,
            "--message", message,
            "--title", title,
            "--interval", interval,
            "--iterations", iterations
        ]
        
        if tags:
            cmd.extend(["--tags", tags])
        
        if priority:
            cmd.extend(["--priority", priority])
            
        # Execute the command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return success page with output
        success_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NTFY Loop Complete</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding-top: 2rem;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                .main-content {{
                    flex: 1;
                }}
                .terminal {{
                    background-color: #1e1e1e;
                    color: #0f0;
                    font-family: monospace;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                }}
                .notification-info {{
                    background-color: #2d3338;
                    border-radius: 6px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container main-content">
                <div class="alert alert-success mt-4" role="alert">
                    <h4 class="alert-heading">NTFY Loop Complete!</h4>
                    <p>Your notification loop to ntfy.sh/{topic} has finished.</p>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">
                        <h5>Loop Configuration</h5>
                    </div>
                    <div class="card-body">
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item"><strong>Topic:</strong> ntfy.sh/{topic}</li>
                            <li class="list-group-item"><strong>Title:</strong> {title}</li>
                            <li class="list-group-item"><strong>Message:</strong> {message}</li>
                            <li class="list-group-item"><strong>Tags:</strong> {tags}</li>
                            <li class="list-group-item"><strong>Priority:</strong> {priority}</li>
                            <li class="list-group-item"><strong>Interval:</strong> {interval} seconds</li>
                            <li class="list-group-item"><strong>Total Messages:</strong> {iterations}</li>
                        </ul>
                    </div>
                </div>
                
                <h5 class="mt-4">Command Output:</h5>
                <div class="terminal">
{result.stdout}
                </div>
                
                <div class="mt-4">
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
            
            <footer class="mt-5">
                <div class="container">
                    <div class="row">
                        <div class="col-md-6">
                            <h5>About efenow's NTFY.sh Sender</h5>
                            <p>efenow's NTFY.sh Sender is a customized tool that lets you send notifications to your phone or desktop using the NTFY.sh service.</p>
                        </div>
                        <div class="col-md-6">
                            <h5>Related Links</h5>
                            <ul class="list-unstyled">
                                <li><a href="https://ntfy.sh" class="text-decoration-none">NTFY.sh Website</a></li>
                                <li><a href="https://docs.ntfy.sh" class="text-decoration-none">NTFY.sh Documentation</a></li>
                            </ul>
                        </div>
                    </div>
                </div>
            </footer>
        </body>
        </html>
        """
        return success_html
        
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}\n\nStdout:\n{e.stdout}\n\nStderr:\n{e.stderr}"
        return f"Error: {error_message}", 500
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/run-curl-loop')
def run_curl_loop():
    """Run the curl loop test workflow and display the results"""
    try:
        # Execute the curl loop test command
        result = subprocess.run(
            [
                sys.executable, 
                "curl_loop.py", 
                "-i", "2", 
                "-n", "2", 
                "-v", 
                "https://httpbin.org/get"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Format the output in a nice HTML page
        output_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Curl Loop Test Results</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <style>
                body {{
                    padding-top: 2rem;
                    min-height: 100vh;
                    display: flex;
                    flex-direction: column;
                }}
                .main-content {{
                    flex: 1;
                }}
                .terminal {{
                    background-color: #1e1e1e;
                    color: #0f0;
                    font-family: monospace;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                    white-space: pre-wrap;
                    max-height: 400px;
                    overflow-y: auto;
                }}
            </style>
        </head>
        <body data-bs-theme="dark">
            <div class="container main-content">
                <h1 class="my-4">Curl Loop Test Results</h1>
                
                <div class="alert alert-success" role="alert">
                    <h4 class="alert-heading">Success!</h4>
                    <p>The Curl Loop test was executed successfully.</p>
                </div>
                
                <h5>Command Output:</h5>
                <div class="terminal">
{result.stdout}
                </div>
                
                <div class="mt-4 mb-5">
                    <a href="/" class="btn btn-primary">Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """
        return output_html
    except Exception as e:
        return f"Error running Curl Loop test: {str(e)}", 500

def main():
    """
    When script is run directly, launch interactive_ntfy.py
    """
    # Get the full path to interactive_ntfy.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "interactive_ntfy.py")
    
    # Check if interactive_ntfy.py exists
    if not os.path.exists(script_path):
        print(f"Error: {script_path} does not exist")
        sys.exit(1)
    
    # Get any command line arguments passed to this script
    args = sys.argv[1:]
    
    # Create the command to run
    cmd = [sys.executable, script_path] + args
    
    try:
        # Execute interactive_ntfy.py as a subprocess
        process = subprocess.run(cmd, check=True)
        sys.exit(process.returncode)
    except KeyboardInterrupt:
        print("\nStopped by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"Error: Command failed with return code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()