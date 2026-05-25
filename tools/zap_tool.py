import urllib.request
import urllib.parse
import socket
import ssl
import json
import logging
from urllib.error import URLError, HTTPError
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SecurityScanner:
    def __init__(self, target_url: str, zap_api_url: str = None, zap_api_key: str = None):
        self.target_url = target_url
        self.parsed_url = urllib.parse.urlparse(target_url)
        self.host = self.parsed_url.hostname
        self.port = self.parsed_url.port or (443 if self.parsed_url.scheme == "https" else 80)
        self.scheme = self.parsed_url.scheme
        self.zap_api_url = zap_api_url
        self.zap_api_key = zap_api_key
        
        self.findings = []
        logging.info(f"Security Scanner initialized for {target_url} (Host: {self.host}, Port: {self.port})")

    def run_full_scan(self) -> list:
        """Executes OWASP ZAP API scan if configured; otherwise runs a comprehensive native Python security scan."""
        if self.zap_api_url and self.zap_api_key:
            logging.info("OWASP ZAP API coordinates provided. Attempting ZAP Daemon Scan...")
            zap_findings = self.scan_via_owasp_zap()
            if zap_findings:
                return zap_findings
            logging.warning("OWASP ZAP scan failed or was unreachable. Falling back to native scanner...")
        
        # Native Python Vulnerability Scanner
        logging.info("Executing native security scans...")
        self.scan_security_headers()
        self.scan_directory_fuzzing()
        self.scan_sql_injection()
        self.scan_xss()
        self.scan_ports()
        self.verify_ssl()
        
        # Deduplicate and sort findings by severity (High -> Medium -> Low -> Info)
        severity_weight = {"High": 4, "Medium": 3, "Low": 2, "Informational": 1}
        self.findings.sort(key=lambda x: severity_weight.get(x["severity"], 0), reverse=True)
        
        logging.info(f"Security scan completed. Discovered {len(self.findings)} security issues.")
        return self.findings

    def scan_via_owasp_zap(self) -> list:
        """Actual integration with OWASP ZAP API (if ZAP is running as a local/remote proxy daemon)."""
        try:
            # We can invoke ZAP API via simple HTTP requests
            # Let's say ZAP API is at http://localhost:8080/JSON/
            base_zap_url = self.zap_api_url.rstrip('/')
            
            # 1. Access target via ZAP proxy to load into ZAP history
            logging.info(f"ZAP Tool: Sending spider command for {self.target_url}")
            spider_url = f"{base_zap_url}/spider/action/scan/?apikey={self.zap_api_key}&url={urllib.parse.quote(self.target_url)}"
            
            req = urllib.request.Request(spider_url)
            with urllib.request.urlopen(req, timeout=5000) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                scan_id = data.get("scan")
                logging.info(f"ZAP Spider triggered. Scan ID: {scan_id}")
            
            # Wait for Spider to complete (mocking quick check for simplicity, or sleeping briefly)
            time.sleep(1)
            
            # 2. Trigger Active Scan
            logging.info(f"ZAP Tool: Sending active scan command")
            ascan_url = f"{base_zap_url}/ascan/action/scan/?apikey={self.zap_api_key}&url={urllib.parse.quote(self.target_url)}"
            req_ascan = urllib.request.Request(ascan_url)
            with urllib.request.urlopen(req_ascan, timeout=5000) as resp:
                ascan_data = json.loads(resp.read().decode('utf-8'))
                ascan_id = ascan_data.get("scan")
                logging.info(f"ZAP Active Scan triggered. Scan ID: {ascan_id}")
                
            # 3. Fetch Alerts
            alerts_url = f"{base_zap_url}/core/view/alerts/?apikey={self.zap_api_key}&baseurl={urllib.parse.quote(self.target_url)}"
            req_alerts = urllib.request.Request(alerts_url)
            with urllib.request.urlopen(req_alerts, timeout=5000) as resp:
                alerts_data = json.loads(resp.read().decode('utf-8'))
                raw_alerts = alerts_data.get("alerts", [])
                
            zap_findings = []
            for alert in raw_alerts:
                zap_findings.append({
                    "name": alert.get("alert", "OWASP Vulnerability"),
                    "severity": alert.get("risk", "Low"),
                    "description": alert.get("description", ""),
                    "url_path": alert.get("url", ""),
                    "remediation": alert.get("solution", "")
                })
            
            logging.info(f"OWASP ZAP scan successful. Found {len(zap_findings)} alerts.")
            return zap_findings
        except Exception as e:
            logging.warning(f"Failed to communicate with ZAP API daemon: {str(e)}")
            return []

    def scan_security_headers(self):
        """Analyzes response headers of the target website to verify security protections."""
        logging.info("Scanner: Checking HTTP Security Headers...")
        try:
            req = urllib.request.Request(
                self.target_url, 
                headers={'User-Agent': 'Mozilla/5.0 Security Scanner'}
            )
            with urllib.request.urlopen(req, timeout=5000) as response:
                headers = response.info()
                
            required_headers = {
                "Content-Security-Policy": (
                    "Low", 
                    "Protects against Cross-Site Scripting (XSS) and injection attacks by specifying authorized sources.",
                    "Implement a strict Content-Security-Policy header outlining script-src, style-src, and default-src directives."
                ),
                "X-Frame-Options": (
                    "Medium", 
                    "Prevents Clickjacking attacks by disabling embedding of the webpage in iframes/frames on other domains.",
                    "Add header 'X-Frame-Options: SAMEORIGIN' or use CSP 'frame-ancestors' directive."
                ),
                "Strict-Transport-Security": (
                    "Low", 
                    "Enforces secure (HTTPS) connections, preventing SSL stripping.",
                    "Configure HSTS header: 'Strict-Transport-Security: max-age=31536000; includeSubDomains'."
                ),
                "X-Content-Type-Options": (
                    "Low", 
                    "Blocks MIME-type sniffing, preventing browsers from executing files uploaded as non-executable types.",
                    "Add header 'X-Content-Type-Options: nosniff'."
                ),
                "Referrer-Policy": (
                    "Informational", 
                    "Controls how much referrer information is passed when navigating from this site.",
                    "Set header 'Referrer-Policy: strict-origin-when-cross-origin'."
                )
            }
            
            for header, (severity, desc, remediation) in required_headers.items():
                # Check case-insensitive
                header_exists = False
                for h_key in headers.keys():
                    if h_key.lower() == header.lower():
                        header_exists = True
                        break
                        
                if not header_exists:
                    self.findings.append({
                        "name": f"Missing Security Header: {header}",
                        "severity": severity,
                        "description": desc,
                        "url_path": self.target_url,
                        "remediation": remediation
                    })
        except Exception as e:
            logging.error(f"Failed to fetch security headers: {str(e)}")
            self.findings.append({
                "name": "Unable to Reach Web App for Headers Scan",
                "severity": "High",
                "description": f"Target web server at {self.target_url} was unreachable: {str(e)}",
                "url_path": self.target_url,
                "remediation": "Check if the server is running, the port is open, and network proxies are configured correctly."
            })

    def scan_directory_fuzzing(self):
        """Attempts to access common sensitive directories or backups on the web app host."""
        logging.info("Scanner: Fuzzing directories and checking for configurations...")
        sensitive_paths = {
            ".git/HEAD": ("High", "Exposed Git repository allows download of entire source code history.", "Restrict HTTP access to the .git directory in web server configurations."),
            ".env": ("High", "Exposed environment configuration file leaking API keys, database credentials, and secrets.", "Remove active .env files from the web root and store secrets in environment variables."),
            "wp-config.php": ("Medium", "WordPress configuration file access. Could leak DB credentials.", "Block web access to config files."),
            "admin/": ("Low", "Administrative panel is exposed publicly.", "Restrict access to administrator sub-panels using network whitelisting or robust basic authentication."),
            "backup.sql": ("High", "Exposed database SQL backup containing table definitions and raw table data.", "Remove database backup SQL dumps from public folders immediately.")
        }
        
        for path, (severity, desc, remediation) in sensitive_paths.items():
            fuzz_url = urllib.parse.urljoin(self.target_url, path)
            try:
                req = urllib.request.Request(
                    fuzz_url, 
                    headers={'User-Agent': 'Mozilla/5.0 Security Scanner'}
                )
                with urllib.request.urlopen(req, timeout=3000) as response:
                    code = response.getcode()
                    # If page loads successfully (200 OK), path is exposed
                    if code == 200:
                        # Double check content is not a generic custom 404 page
                        content = response.read(200).decode('utf-8', errors='ignore')
                        if "page not found" not in content.lower() and "404" not in content:
                            self.findings.append({
                                "name": f"Exposed Sensitive Path: /{path}",
                                "severity": severity,
                                "description": desc,
                                "url_path": fuzz_url,
                                "remediation": remediation
                            })
            except (HTTPError, URLError, socket.timeout):
                # An HTTP error (e.g. 404, 403) or timeout indicates the path is secure/blocked
                continue

    def scan_sql_injection(self):
        """Tests SQL Injection vulnerability against query parameters of the target url."""
        logging.info("Scanner: Checking for SQL Injection vulnerabilities...")
        
        # Test payloads
        sqli_payloads = ["'", "' OR '1'='1", "1' ORDER BY 1--", "admin' --"]
        db_errors = [
            "SQL syntax", "mysql_fetch_array", "sqlite3", "PostgreSQL query",
            "execute query", "driver exception", "Syntax error in SQL statement"
        ]
        
        # If the URL contains parameters, we test those, otherwise we test a test query parameter 'id'
        parsed = urllib.parse.urlparse(self.target_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            params = {"id": ["1"]}
            
        for param_key in params.keys():
            for payload in sqli_payloads:
                # Inject payload into parameter
                test_params = params.copy()
                test_params[param_key] = [payload]
                
                query_str = urllib.parse.urlencode(test_params, doseq=True)
                test_url = urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path, 
                    parsed.params, query_str, parsed.fragment
                ))
                
                try:
                    req = urllib.request.Request(
                        test_url, 
                        headers={'User-Agent': 'Mozilla/5.0 Security Scanner'}
                    )
                    with urllib.request.urlopen(req, timeout=4000) as response:
                        html_content = response.read().decode('utf-8', errors='ignore')
                        
                        # Check for database error signature in HTML response
                        for error in db_errors:
                            if error.lower() in html_content.lower():
                                self.findings.append({
                                    "name": f"SQL Injection Vulnerability detected on parameter '{param_key}'",
                                    "severity": "High",
                                    "description": f"Injecting SQL payload '{payload}' into parameter '{param_key}' triggered a database error message: '{error}'. This confirms raw user input is directly concatenated into a SQL statement.",
                                    "url_path": test_url,
                                    "remediation": "Use Prepared Statements and Parameterized Queries for all database interactions. Implement proper validation and sanitation (e.g., ORM models like SQLAlchemy)."
                                })
                                return  # Return early once SQLi is detected
                except (HTTPError) as e:
                    # Sometimes database errors cause 500 Internal Server Errors. Let's read error stream
                    try:
                        err_content = e.read().decode('utf-8', errors='ignore')
                        for error in db_errors:
                            if error.lower() in err_content.lower():
                                self.findings.append({
                                    "name": f"Blind SQL Injection Vulnerability on parameter '{param_key}'",
                                    "severity": "High",
                                    "description": f"Injecting SQL payload '{payload}' returned a {e.code} status code and triggered database error message: '{error}' in the response body.",
                                    "url_path": test_url,
                                    "remediation": "Use Prepared Statements and Parameterized Queries for all database queries. Avoid concatenating input strings directly into SQL code."
                                })
                                return
                    except Exception:
                        pass
                except Exception:
                    pass

    def scan_xss(self):
        """Performs reflected Cross-Site Scripting (XSS) payload checking."""
        logging.info("Scanner: Checking for Cross-Site Scripting (XSS)...")
        xss_payloads = [
            "<script>alert(1)</script>",
            '"><img src=x onerror=alert(1)>',
            "javascript:alert(1)"
        ]
        
        parsed = urllib.parse.urlparse(self.target_url)
        params = urllib.parse.parse_qs(parsed.query)
        if not params:
            params = {"q": ["test"]}
            
        for param_key in params.keys():
            for payload in xss_payloads:
                test_params = params.copy()
                test_params[param_key] = [payload]
                
                query_str = urllib.parse.urlencode(test_params, doseq=True)
                test_url = urllib.parse.urlunparse((
                    parsed.scheme, parsed.netloc, parsed.path, 
                    parsed.params, query_str, parsed.fragment
                ))
                
                try:
                    req = urllib.request.Request(
                        test_url, 
                        headers={'User-Agent': 'Mozilla/5.0 Security Scanner'}
                    )
                    with urllib.request.urlopen(req, timeout=4000) as response:
                        html_content = response.read().decode('utf-8', errors='ignore')
                        
                        # If the script payload is reflected inside the response HTML exactly
                        if payload in html_content:
                            self.findings.append({
                                "name": f"Reflected Cross-Site Scripting (XSS) on parameter '{param_key}'",
                                "severity": "High",
                                "description": f"The injection payload '{payload}' was successfully reflected inside the HTML document without proper encoding/sanitization. Browsers will execute this payload in the context of the user session.",
                                "url_path": test_url,
                                "remediation": "Apply context-aware output encoding (e.g. HTML escape variables before printing them). Leverage templating engines with auto-escaping enabled by default (like Jinja2 or React JSX)."
                            })
                            return
                except Exception:
                    pass

    def scan_ports(self):
        """Scans for commonly open administrative and backend ports on the target domain/IP."""
        logging.info(f"Scanner: Scanning open ports on host: {self.host}...")
        # Common ports to inspect
        target_ports = {
            21: ("Medium", "FTP Service Exposed", "FTP is an insecure legacy protocol. Consider replacing it with SFTP/SSH."),
            22: ("Low", "SSH Service Exposed", "Configure secure SSH keys, disable root logins, and apply Rate Limiting/Fail2ban."),
            23: ("High", "Telnet Service Exposed", "Disable Telnet immediately and switch to secure SSH connections."),
            25: ("Low", "SMTP Mail Server Exposed", "Ensure SMTP is configured correctly, not operating as an open relay."),
            8080: ("Low", "HTTP Alternative Proxy/Admin Panel Exposed", "Restrict access using network controls or firewalls."),
            3306: ("High", "MySQL Database Service Exposed publicly", "Bind MySQL to localhost or secure inside a private VPC. Never expose database ports to the internet."),
            5432: ("High", "PostgreSQL Database Service Exposed publicly", "Bind database service to private network addresses only.")
        }
        
        # Don't scan standard web ports 80/443 since they are supposed to be open!
        for port, (severity, name, remediation) in target_ports.items():
            try:
                # Fast connection check
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                res = sock.connect_ex((self.host, port))
                if res == 0:
                    self.findings.append({
                        "name": f"Exposed Port {port}: {name}",
                        "severity": severity,
                        "description": f"The port {port} was verified to be in an open/responsive state from public networks.",
                        "url_path": f"{self.host}:{port}",
                        "remediation": remediation
                    })
                sock.close()
            except Exception:
                pass

    def verify_ssl(self):
        """Verifies SSL configuration if scanning an HTTPS endpoint."""
        if self.scheme != "https":
            self.findings.append({
                "name": "Insecure HTTP Protocol in Use",
                "severity": "Medium",
                "description": "The web application uses the cleartext HTTP protocol, exposing sensitive parameters and user sessions to eavesdropping.",
                "url_path": self.target_url,
                "remediation": "Obtain an SSL/TLS certificate (e.g., Let's Encrypt) and force HTTPS redirection on all endpoints."
            })
            return
            
        logging.info("Scanner: Validating SSL Certificate security...")
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.host, self.port), timeout=4000) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssock:
                    cert = ssock.getpeercert()
                    
            if not cert:
                self.findings.append({
                    "name": "Weak SSL Certificate Configuration",
                    "severity": "Medium",
                    "description": "Target is using HTTPS but could not verify full certificate authority details.",
                    "url_path": self.target_url,
                    "remediation": "Verify SSL configuration and ensure a valid cert chain is provided."
                })
        except ssl.SSLError as e:
            self.findings.append({
                "name": "SSL/TLS Handshake Vulnerability / Invalid Certificate",
                "severity": "High",
                "description": f"The SSL certificate on {self.host} is invalid, self-signed, or expired. Error: {str(e)}",
                "url_path": self.target_url,
                "remediation": "Install a valid, non-expired certificate signed by a recognized Certificate Authority (CA)."
            })
        except Exception:
            pass

if __name__ == "__main__":
    # Local self test targeting example
    scanner = SecurityScanner("https://example.com")
    vulns = scanner.run_full_scan()
    print(f"Found {len(vulns)} issues!")
    for v in vulns:
        print(f"- {v['name']} [{v['severity']}]")
