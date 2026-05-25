import os
import argparse
import sys
import logging
from memory.database import create_scan_history, save_agent_interaction, update_scan_status, get_scan_details
from agents.test_agent import TestAgent
from agents.security_agent import SecurityAgent
from agents.report_agent import ReportAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("PipelineOrchestrator")

def run_agentic_pipeline(target_url: str, feature_desc: str = "", zap_url: str = None, zap_key: str = None, api_key: str = None, model: str = "gpt-4o") -> dict:
    """Executes the full continuous security and quality assurance agentic pipeline.
    Ensures state handoffs, short-term and long-term memory logging, and final document publication.
    """
    logger.info("Initializing Agentic QA & Security Pipeline execution...")
    
    # 1. Establish new scan run inside SQLite memory
    try:
        scan_id = create_scan_history(target_url)
        logger.info(f"Pipeline Run Session successfully registered. Scan ID: #{scan_id}")
    except Exception as db_err:
        logger.error(f"Failed to initialize database log: {str(db_err)}")
        raise
        
    save_agent_interaction(scan_id, "Pipeline Orchestrator", f"Continuous integration pipeline triggered targeting URL: {target_url}")
    
    try:
        # 2. Instantiate collaborating agents
        logger.info("Instantiating AI Agents (Test Case Generator, Security Analyst, Report Compiler)...")
        
        test_agent = TestAgent(api_key=api_key, model=model)
        security_agent = SecurityAgent(api_key=api_key, model=model)
        report_agent = ReportAgent(api_key=api_key, model=model)
        
        # 3. Trigger QA Test Case Agent (incorporates Playwright tool under-the-hood)
        logger.info("Agent Phase 1: Activating Test Case Generator Agent...")
        save_agent_interaction(scan_id, "Pipeline Orchestrator", "Activating Lead QA Agent. Scraping page layout and designing test suite.")
        
        test_cases = test_agent.analyze_and_generate_tests(target_url, feature_desc)
        logger.info(f"Agent Phase 1: Completed. Designed {len(test_cases)} verification scenarios.")
        
        save_agent_interaction(
            scan_id, 
            test_agent.name, 
            f"DOM analysis complete. Structured JSON test suite composed containing {len(test_cases)} cases. Passing to security track."
        )
        
        # 4. Trigger Security Scan Agent (incorporates ZAP tool + Native scans under-the-hood)
        logger.info("Agent Phase 2: Activating Security Scan Agent...")
        save_agent_interaction(scan_id, "Pipeline Orchestrator", "Activating Security Agent. Deploying scanners and fuzzers.")
        
        vulnerabilities = security_agent.scan_and_analyze_vulnerabilities(target_url, zap_url, zap_key)
        logger.info(f"Agent Phase 2: Completed. Found {len(vulnerabilities)} vulnerabilities.")
        
        save_agent_interaction(
            scan_id, 
            security_agent.name, 
            f"Vulnerability scanner completed with {len(vulnerabilities)} issues identified and enriched. Handing off to Report Agent."
        )
        
        # 5. Trigger Report Agent to store memory, write docx, and finalize status
        logger.info("Agent Phase 3: Activating Report Compiler Agent for consolidation...")
        docx_report_path = report_agent.compile_pipeline_findings(
            scan_id=scan_id,
            target_url=target_url,
            test_cases=test_cases,
            vulnerabilities=vulnerabilities
        )
        
        logger.info(f"Pipeline Run successfully completed! DOCX Report compiled: {docx_report_path}")
        
        # Retrieve complete scan results from database for return dictionary
        scan_results = get_scan_details(scan_id)
        scan_results["docx_path"] = docx_report_path
        
        return scan_results

    except Exception as pipeline_err:
        logger.error(f"Fatal crash inside pipeline execution: {str(pipeline_err)}")
        update_scan_status(scan_id, "FAILED")
        save_agent_interaction(scan_id, "Pipeline Orchestrator", f"FATAL ERROR: Pipeline aborted due to exception: {str(pipeline_err)}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Multi-Agent QA and Security Testing Pipeline CLI")
    parser.add_argument("--url", type=str, default="http://localhost:5000", help="Target URL to scrape, test, and scan")
    parser.add_argument("--feature", type=str, default="", help="Feature requirements text or file path to feature specifications")
    parser.add_argument("--zap-url", type=str, default=None, help="OWASP ZAP API endpoint URL")
    parser.add_argument("--zap-key", type=str, default=None, help="OWASP ZAP API authorization key")
    parser.add_argument("--api-key", type=str, default=None, help="OpenAI secret API key")
    parser.add_argument("--model", type=str, default="gpt-4o", help="OpenAI LLM engine selection")
    
    args = parser.parse_args()
    
    # Check for feature file if a filepath is provided
    feature_text = args.feature
    if feature_text and os.path.exists(feature_text):
        try:
            with open(feature_text, 'r', encoding='utf-8') as f:
                feature_text = f.read()
        except Exception as e:
            logger.error(f"Failed to read feature description file: {str(e)}")
            sys.exit(1)
            
    # Read OpenAI Key from environment if not passed explicitly in CLI
    openai_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not openai_key:
        logger.error(
            "ERROR: OpenAI API Key is missing!\n"
            "Please export OPENAI_API_KEY=your_key or pass it using the --api-key argument."
        )
        sys.exit(1)
        
    try:
        results = run_agentic_pipeline(
            target_url=args.url,
            feature_desc=feature_text,
            zap_url=args.zap_url,
            zap_key=args.zap_key,
            api_key=openai_key,
            model=args.model
        )
        
        print("\n" + "="*60)
        print("          PIPELINE EXECUTION SUCCESSFUL")
        print("="*60)
        print(f"Target URL:         {results['target_url']}")
        print(f"Vulnerabilities:    {len(results['vulnerabilities'])} issues cataloged")
        print(f"Test Cases:         {len(results['test_cases'])} scenarios designed")
        print(f"Report Location:    {results['docx_path']}")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.critical(f"CLI Orchestration execution crashed: {str(e)}")
        sys.exit(1)
