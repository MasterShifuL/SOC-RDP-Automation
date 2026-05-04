from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import subprocess
import datetime

HOST = "0.0.0.0"
PORT = 8080

class Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Disable default noisy logging
        return

    def do_GET(self):
        try:
            # Parse query
            parsed_path = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_path.query)

            user = params.get("user", [""])[0].strip()

            print(f"[{datetime.datetime.now()}] Incoming request: {self.path}")

            # Validate input
            if not user:
                self.respond(400, "ERROR: No user provided")
                return

            # Security: prevent weird injection characters
            if not user.isalnum():
                self.respond(400, f"ERROR: Invalid username '{user}'")
                return

            print(f"[INFO] Processing disable request for user: {user}")

            # Build PowerShell command
            cmd = [
                "powershell",
                "-ExecutionPolicy", "Bypass",
                "-File", "C:\\scripts\\disable_user.ps1",
                "-username", user
            ]

            # Execute with timeout
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                output = result.stdout.strip() + "\n" + result.stderr.strip()

                if result.returncode == 0:
                    response = f"SUCCESS: {output}"
                    print(f"[SUCCESS] {response}")
                    self.respond(200, response)
                else:
                    response = f"ERROR: {output}"
                    print(f"[ERROR] {response}")
                    self.respond(500, response)

            except subprocess.TimeoutExpired:
                print("[ERROR] PowerShell script timeout")
                self.respond(500, "ERROR: Script execution timeout")

        except Exception as e:
            print(f"[CRITICAL] {str(e)}")
            self.respond(500, f"ERROR: {str(e)}")

    def respond(self, status, message):
        self.send_response(status)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(message.encode())


if __name__ == "__main__":
    print(f"[START] Server running on {HOST}:{PORT}")
    server = HTTPServer((HOST, PORT), Handler)
    server.serve_forever()
