import http.server
import socketserver
import urllib.parse
import re

PORT = 5000

class VulnerableHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    
    # Override log_message to keep terminal output clean
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # 1. Exposed Git Directory Check
        if path == "/.git/HEAD":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            # Purposefully missing security headers!
            self.end_headers()
            self.wfile.write(b"ref: refs/heads/main\n")
            return

        # 2. Exposed Env Configurations
        elif path == "/.env":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            env_content = (
                "# Exposed secrets configuration!\n"
                "DB_USER=admin_db\n"
                "DB_PASS=SuperSecurePass123_dont_share!\n"
                "OPENAI_API_KEY=sk-proj-T1m3ToSc4nS3cur3lyW1thAntigravity10293\n"
            )
            self.wfile.write(env_content.encode("utf-8"))
            return

        # 3. Reflected XSS Vulnerability in Search query parameter
        elif path == "/search":
            q = query_params.get("q", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            # Vulnerable reflection without HTML escaping!
            response_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Search Portal</title>
                <style>
                    body {{ font-family: sans-serif; background-color: #f7f9fa; margin: 40px; color: #333; }}
                    .box {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    a {{ color: #1f4e79; text-decoration: none; }}
                </style>
            </head>
            <body>
                <div class="box">
                    <h2>Search Results</h2>
                    <p>You searched for: <b>{q}</b></p>
                    <hr>
                    <p>No results found for your query. Try searching for "products".</p>
                    <br>
                    <a href="/">&larr; Return to main portal</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode("utf-8"))
            return

        # 4. SQL Injection Vulnerability in product feedback lookup
        elif path == "/feedback":
            product_id = query_params.get("id", [""])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            # Trigger standard database error output if SQL syntax single quote is injected!
            if "'" in product_id:
                error_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>500 Internal Database Error</title></head>
                <body style="font-family: monospace; background: #fff; padding: 30px;">
                    <h3>Internal Server Error</h3>
                    <p>An unhandled database exception occurred while executing raw SQL queries.</p>
                    <div style="background: #fde8e8; border: 1px solid #f8b4b4; padding: 15px; color: #9c0006; border-radius: 4px;">
                        <b>[SQLITE3 EXCEPTION ERROR]:</b> syntax error near "{product_id}": statement was not compiled correctly. 
                        Query attempted: SELECT * FROM reviews WHERE product_id = '{product_id}';
                    </div>
                    <hr>
                    <a href="/">&larr; Go Back</a>
                </body>
                </html>
                """
                self.wfile.write(error_html.encode("utf-8"))
                return

            response_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Product Reviews Feedback</title>
                <style>
                    body {{ font-family: sans-serif; background-color: #f7f9fa; margin: 40px; }}
                    .card {{ background: white; padding: 20px; border-radius: 8px; max-width: 600px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                    input {{ padding: 8px; border: 1px solid #ccc; width: 100px; margin-right: 10px; border-radius: 4px; }}
                    button {{ padding: 8px 15px; background: #1f4e79; color: white; border: none; cursor: pointer; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Reviews Lookup</h2>
                    <p>Lookup rating scores by product ID index.</p>
                    <form action="/feedback" method="get">
                        <label>Product ID Reference: </label>
                        <input type="text" name="id" value="{product_id or '1'}">
                        <button type="submit">Query Database</button>
                    </form>
                    <br>
                    <div style="background: #eef2f5; padding: 15px; border-radius: 4px;">
                        <b>Result:</b> {"Product ID #" + product_id + " score: 4.8/5.0 Stars" if product_id else "No ID queried."}
                    </div>
                    <br>
                    <a href="/" style="color: #1f4e79; text-decoration: none;">&larr; Return to main portal</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode("utf-8"))
            return

        # 5. Serve main index page
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            index_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Secure Demo Bank Portal</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; background: #f0f2f5; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
                    .container { background: white; border-radius: 12px; width: 500px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); padding: 40px; margin: 20px; }
                    h1 { color: #1f4e79; font-size: 28px; margin-bottom: 5px; }
                    p { color: #666; font-size: 14px; margin-top: 0; margin-bottom: 25px; }
                    .form-group { margin-bottom: 18px; display: flex; flex-direction: column; }
                    label { font-size: 13px; font-weight: bold; margin-bottom: 6px; color: #444; }
                    input[type="text"], input[type="password"] { padding: 10px; border: 1px solid #ccd0d5; border-radius: 6px; font-size: 14px; }
                    button { padding: 12px; background: #1f4e79; color: white; border: none; font-size: 15px; font-weight: bold; border-radius: 6px; cursor: pointer; transition: background 0.2s; }
                    button:hover { background: #163654; }
                    .nav-links { display: flex; gap: 15px; justify-content: center; margin-top: 20px; font-size: 13px; }
                    .nav-links a { color: #1f4e79; text-decoration: none; font-weight: bold; }
                    .nav-links a:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Secure Demo Bank</h1>
                    <p>Academic testing portal containing simulated forms and inputs.</p>
                    
                    <form action="/login" method="post">
                        <div class="form-group">
                            <label for="user">Client Login ID (Email):</label>
                            <input type="text" id="user" name="username" placeholder="enter client email">
                        </div>
                        <div class="form-group">
                            <label for="pass">Access Password:</label>
                            <input type="password" id="pass" name="password" placeholder="enter secret key">
                        </div>
                        <button type="submit">Verify Credentials</button>
                    </form>
                    
                    <div class="nav-links">
                        <a href="/search?q=test">Search Portal</a>
                        <a href="/feedback">Reviews Lookup</a>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(index_html.encode("utf-8"))
            return

    def do_POST(self):
        # 1. Login form submission simulation
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            
            response_html = """
            <!DOCTYPE html>
            <html>
            <head><title>Access Processed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px; background: #f7f9fa;">
                <div style="background: white; padding: 30px; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h2 style="color: #2e7d32;">Authentication Cycle Completed</h2>
                    <p>Creds submitted successfully. Handshake validation in progress...</p>
                    <a href="/" style="color: #1f4e79; text-decoration: none; font-weight: bold;">&larr; Go Back</a>
                </div>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode("utf-8"))
            return

def run_server():
    server_address = ('', PORT)
    # Allow address reuse to prevent "Address already in use" errors during quick restarts
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, VulnerableHTTPRequestHandler) as httpd:
        print(f"Vulnerable Target Demo Application running at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
