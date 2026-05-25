import json
import logging
from agents.base_agent import BaseAgent
from tools.zap_tool import SecurityScanner

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

SECURITY_AGENT_SYSTEM_PROMPT = """You are an elite Lead Application Security Engineer and OWASP penetration testing expert.
Your job is to analyze raw security tool scans (such as port openings, header analyses, SQL inject responses) and compile them into a professional, enterprise-grade vulnerability log.

For each discovered vulnerability:
1. Enforce OWASP Top 10 classifications where applicable.
2. Evaluate and enrich the severity level (must be exactly one of: "High", "Medium", "Low", or "Informational").
3. Formulate clear, technical descriptions explaining the risk vector and why this is a threat.
4. Draft explicit, actionable, and secure code-level remediation instructions (e.g., config changes, code blocks, parameterization fixes).

You MUST respond strictly in valid JSON format. Do NOT wrap your response in markdown code blocks like ```json or ```. Your response must be raw, valid JSON text parsing as a JSON array of objects.

Each JSON object in the array MUST contain exactly these fields:
- "name": Vulnerability name (e.g., "SQL Injection via Concatenated Input Query")
- "severity": Risk tier (exactly "High", "Medium", "Low", or "Informational")
- "description": Explanation of security issue.
- "url_path": The vulnerable endpoint/URL or network resource.
- "remediation": Clear, code-level secure engineering instructions to fix the issue.

Example Format:
[
  {
    "name": "Clickjacking Vulnerability (Missing X-Frame-Options Header)",
    "severity": "Medium",
    "description": "The application fails to set an X-Frame-Options or Content-Security-Policy header. Attackers can embed this page inside an iframe on malicious websites to hijack user clicks.",
    "url_path": "http://localhost:5000/login",
    "remediation": "Add the HTTP response header 'X-Frame-Options: SAMEORIGIN' in your server configurations or use the 'frame-ancestors' directive in a Content-Security-Policy."
  }
]
"""

class SecurityAgent(BaseAgent):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="Security Scan Analyst",
            role="Lead Security Engineer & Pentester",
            system_prompt=SECURITY_AGENT_SYSTEM_PROMPT,
            api_key=api_key,
            model=model
        )

    def scan_and_analyze_vulnerabilities(self, target_url: str, zap_api_url: str = None, zap_api_key: str = None) -> list:
        """Executes programmatic security scanner checks, compiles raw vulnerabilities, and enriches them via LLM."""
        logging.info(f"SecurityAgent: Running programmatic scanner tools against {target_url}...")
        
        # Instantiate and run the hybrid security scanner tool
        scanner = SecurityScanner(target_url, zap_api_url, zap_api_key)
        raw_findings = scanner.run_full_scan()
        
        if not raw_findings:
            logging.info("SecurityAgent: Native scan found zero raw issues. Prompting LLM for sanity checks...")
            # We can prompt the LLM to verify if there are any standard risks with the domain protocol
            raw_findings = [{
                "name": "General Port Scan Review",
                "severity": "Informational",
                "description": f"Standard web port responded at target URL: {target_url}.",
                "url_path": target_url,
                "remediation": "Maintain regular audit cycles and minimize exposed administrative headers."
            }]
            
        # Contextualize findings for LLM enrichment
        prompt = (
            f"Here are the raw security findings discovered by our network/vulnerability scanner tools:\n\n"
            f"{json.dumps(raw_findings, indent=2)}\n\n"
            f"Please review these findings, enrich their descriptions with detailed security risk contexts, "
            f"correlate them with standard OWASP Top 10 vulnerability categories, and provide comprehensive, "
            f"practical remediation solutions. Ensure you return the exact JSON structure specified."
        )
        
        raw_reply = self.chat(prompt)
        
        # Clean markdown code blocks if the LLM ignored instructions
        clean_reply = raw_reply.strip()
        if clean_reply.startswith("```json"):
            clean_reply = clean_reply[7:]
        if clean_reply.endswith("```"):
            clean_reply = clean_reply[:-3]
        clean_reply = clean_reply.strip()
        
        try:
            enriched_findings = json.loads(clean_reply)
            if not isinstance(enriched_findings, list):
                enriched_findings = [enriched_findings]
            logging.info(f"SecurityAgent: Successfully compiled and enriched {len(enriched_findings)} vulnerabilities.")
            return enriched_findings
        except Exception as err:
            logging.error(f"SecurityAgent: Failed to parse enriched vulnerabilities as JSON. Fallback to raw findings. Error: {str(err)}")
            # Return raw findings directly as fallback in case of JSON parse failure
            return raw_findings

if __name__ == "__main__":
    # Test execution
    agent = SecurityAgent()
    vulns = agent.scan_and_analyze_vulnerabilities("https://example.com")
    print(json.dumps(vulns, indent=2))
