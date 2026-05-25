import logging
import json
from datetime import datetime
from agents.base_agent import BaseAgent
from memory.database import save_test_case, save_vulnerability, save_agent_interaction, update_scan_status, get_scan_details
from tools.report_tool import generate_docx_report

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

REPORT_SYSTEM_PROMPT = """You are a senior Principal QA Consultant and Technical Security Writer. 
Your responsibility is to synthesize detailed test suites and vulnerability scan reports, write comprehensive executive summaries, and produce high-quality, professional technical audits.

Your executive summaries should:
1. Clearly contextualize the scan, target URL, and scope of operations.
2. Outline key high-level findings (e.g. how many critical test cases were designed and how many severe vulnerabilities were detected).
3. Offer an analytical risk-posture assessment of the target website (e.g., highly vulnerable, moderately secured, or hardened).
4. Provide high-level recommendations for immediate engineering priorities.

Always write in a highly professional, objective, academic-grade tone suitable for CTOs, CISOs, and QA directors.
"""

class ReportAgent(BaseAgent):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="Report Compiler Agent",
            role="Principal Quality & Security Technical Consultant",
            system_prompt=REPORT_SYSTEM_PROMPT,
            api_key=api_key,
            model=model
        )

    def compile_pipeline_findings(self, scan_id: int, target_url: str, test_cases: list, vulnerabilities: list) -> str:
        """Consolidates findings from test case and security agents, saves them in SQLite memory, and builds the Word DOCX report."""
        logging.info(f"ReportAgent: Initiating consolidation and database persistence for scan ID #{scan_id}")
        
        # 1. Log Agent Handoffs in DB (Short-term / Audit Context)
        save_agent_interaction(
            scan_id, 
            "System Orchestrator", 
            f"Handing off data to Report Compiler Agent for consolidation. Packages: {len(test_cases)} tests and {len(vulnerabilities)} vulnerabilities."
        )
        
        # 2. Save Test Cases in SQLite DB memory
        logging.info("ReportAgent: Persisting generated test cases to database...")
        for tc in test_cases:
            save_test_case(
                scan_id=scan_id,
                category=tc.get("category", "Positive"),
                test_name=tc.get("test_name", "QA Validation"),
                description=tc.get("description", ""),
                steps=tc.get("steps", ""),
                expected_result=tc.get("expected_result", "")
            )
            
        # 3. Save Vulnerabilities in SQLite DB memory
        logging.info("ReportAgent: Persisting vulnerability logs to database...")
        for v in vulnerabilities:
            save_vulnerability(
                scan_id=scan_id,
                name=v.get("name", "Vulnerability"),
                severity=v.get("severity", "Low"),
                description=v.get("description", ""),
                url_path=v.get("url_path", ""),
                remediation=v.get("remediation", "")
            )
            
        # 4. Generate AI Executive Summary using LLM
        logging.info("ReportAgent: Authoring executive summary via LLM reasoning...")
        prompt = (
            f"Please write a comprehensive, professional executive summary report for the QA & Security scan.\n"
            f"Target URL: {target_url}\n"
            f"Scan Reference ID: #{scan_id}\n\n"
            f"Test Cases Cataloged ({len(test_cases)}):\n{json.dumps(test_cases, indent=2)}\n\n"
            f"Security Risks Detected ({len(vulnerabilities)}):\n{json.dumps(vulnerabilities, indent=2)}\n\n"
            f"Format your response as a polished executive summary ready to be embedded. Include sections for: "
            f"Scope of Assessment, Summary of Key Findings, Strategic Risk Posture, and Critical Remediation Roadmaps."
        )
        
        exec_summary = self.chat(prompt, temperature=0.3)
        
        # 5. Log the summary inside agent interactions database for permanent retrieval
        save_agent_interaction(scan_id, self.name, f"Completed Executive Audit Summary:\n\n{exec_summary}")
        
        # 6. Extract metrics for scan history table update
        high_count = sum(1 for v in vulnerabilities if v.get("severity") == "High")
        med_count = sum(1 for v in vulnerabilities if v.get("severity") == "Medium")
        low_count = sum(1 for v in vulnerabilities if v.get("severity") == "Low")
        info_count = sum(1 for v in vulnerabilities if v.get("severity") == "Informational")
        
        vuln_metrics = {
            "High": high_count,
            "Medium": med_count,
            "Low": low_count,
            "Informational": info_count,
            "Total": len(vulnerabilities)
        }
        
        test_categories = [tc.get("category", "Positive") for tc in test_cases]
        test_metrics = {
            "Positive": test_categories.count("Positive"),
            "Negative": test_categories.count("Negative"),
            "Edge Case": test_categories.count("Edge Case"),
            "Total": len(test_cases)
        }
        
        # 7. Update database scan status to COMPLETED with metrics
        update_scan_status(
            scan_id=scan_id,
            status="COMPLETED",
            summary_vulns=vuln_metrics,
            summary_tests=test_metrics
        )
        
        # 8. Retrieve complete consolidated scan payload (including DB IDs) and write the Word Document
        full_scan_data = get_scan_details(scan_id)
        logging.info("ReportAgent: Compiling professional Word report layout (DOCX)...")
        docx_path = generate_docx_report(full_scan_data)
        
        save_agent_interaction(
            scan_id, 
            "System Orchestrator", 
            f"Pipeline run successfully concluded. Document report archived at: {docx_path}"
        )
        
        return docx_path
