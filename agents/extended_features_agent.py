import json
import logging
from agents.base_agent import BaseAgent
from tools.playwright_tool import scrape_page_structure

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BDD_SYSTEM_PROMPT = """You are an expert QA Engineer specializing in Behavior-Driven Development (BDD). 
Your task is to take a set of functional test cases and target page structures, and convert them into beautifully structured Cucumber / Gherkin BDD Feature Files.

Each feature file must follow standard Gherkin syntax:
- Feature: [Title]
- Background: [Setup steps, if applicable]
- Scenario: [Name of scenario]
- Given [preconditions]
- When [actions]
- Then [expected outcomes]
- And / But [optional extra steps]

Highlight best practices in BDD design, including clear scenarios, readable steps, and well-defined parameters.
"""

PLAYWRIGHT_SYSTEM_PROMPT = """You are an elite SDET Automation Engineer specializing in Python Playwright.
Your task is to generate complete, modern, robust, and asynchronous Playwright test scripts in Python based on the given test cases and webpage DOM structure.

Ensure the generated script includes:
1. Asynchronous syntax using `asyncio` and `async_playwright`.
2. Proper setup and teardown actions.
3. Accurate locator methods (e.g., `page.locator(...)`, `page.get_by_role(...)`, `page.get_by_label(...)`, input fills, and button clicks).
4. Assertions (e.g., checking text visibility, input values, page URLs).
5. Error handling and wait conditions for reliability under asynchronous rendering.
6. A self-contained, executable structure with clear comments.
"""

COVERAGE_SYSTEM_PROMPT = """You are a Senior QA Director and Security Compliance Officer.
Your task is to perform a comprehensive Coverage Gap Analysis. You will compare:
1. The target web application structure and identified forms/inputs.
2. The current designed test cases.
3. The discovered security vulnerabilities.

Generate a highly structured audit report including:
- **Coverage Statistics**: Numerical estimate (%) of covered fields, forms, and paths.
- **Identified Coverage Gaps**: Critical areas, user stories, or fields that are not fully validated by the current test suite.
- **Vulnerability Impact Mapping**: How security vulnerabilities correlate to functional test gaps.
- **Actionable Remediation Checklist**: Step-by-step additions to the test suite to achieve 100% QA coverage and robust regression safety.
"""

class ExtendedFeaturesAgent(BaseAgent):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="Extended QA Suite Agent",
            role="SDET Architect & BDD Specialist",
            system_prompt="You are a versatile QA and DevSecOps engineering assistant.",
            api_key=api_key,
            model=model
        )

    def generate_bdd_scenarios(self, target_url: str, test_cases: list) -> str:
        """Generates Gherkin / BDD scenarios from existing test cases and page specifications."""
        logging.info("ExtendedFeaturesAgent: Generating BDD test scenarios...")
        self.system_prompt = BDD_SYSTEM_PROMPT
        
        prompt = f"Target Application URL: {target_url}\n\n"
        prompt += "Here are the designed test cases to convert to Gherkin BDD format:\n"
        prompt += json.dumps(test_cases, indent=2)
        prompt += "\n\nConvert these test cases into professional Cucumber/Gherkin Feature files. Group related scenarios under relevant Feature headers."
        
        return self.chat(prompt)

    def generate_playwright_script(self, target_url: str, test_cases: list) -> str:
        """Generates ready-to-run Python Playwright code blocks corresponding to the test cases."""
        logging.info("ExtendedFeaturesAgent: Generating Playwright automation script...")
        self.system_prompt = PLAYWRIGHT_SYSTEM_PROMPT
        
        # Try scraping structure to get precise locators
        dom_structure = {}
        try:
            dom_structure = scrape_page_structure(target_url)
        except Exception as e:
            logging.warning(f"Failed to scrape structure for Playwright generation: {e}")

        prompt = f"Target Application URL: {target_url}\n"
        prompt += f"Discovered DOM Features:\n"
        prompt += f"- Forms: {json.dumps(dom_structure.get('forms', []))}\n"
        prompt += f"- Inputs: {json.dumps(dom_structure.get('inputs', []))}\n"
        prompt += f"- Buttons: {json.dumps(dom_structure.get('buttons', []))}\n\n"
        prompt += "Here are the designed test cases to build automation for:\n"
        prompt += json.dumps(test_cases, indent=2)
        prompt += "\n\nGenerate a single, robust, clean, and self-contained asynchronous Python Playwright script that automates these scenarios."
        
        return self.chat(prompt)

    def perform_coverage_gap_analysis(self, target_url: str, test_cases: list, vulnerabilities: list) -> str:
        """Compares target page structure, existing tests, and vulnerabilities to report test coverage gap."""
        logging.info("ExtendedFeaturesAgent: Performing Coverage Gap Analysis...")
        self.system_prompt = COVERAGE_SYSTEM_PROMPT
        
        dom_structure = {}
        try:
            dom_structure = scrape_page_structure(target_url)
        except Exception as e:
            logging.warning(f"Failed to scrape structure for Coverage Gap analysis: {e}")

        prompt = f"Target Application URL: {target_url}\n"
        prompt += f"Application DOM Structure Elements:\n"
        prompt += f"- Forms: {json.dumps(dom_structure.get('forms', []))}\n"
        prompt += f"- Inputs: {json.dumps(dom_structure.get('inputs', []))}\n"
        prompt += f"- Buttons: {json.dumps(dom_structure.get('buttons', []))}\n\n"
        prompt += f"Currently Configured QA Test Suite Scenarios:\n"
        prompt += json.dumps(test_cases, indent=2) + "\n\n"
        prompt += f"Discovered Security Vulnerabilities:\n"
        prompt += json.dumps(vulnerabilities, indent=2) + "\n\n"
        prompt += "Please conduct a rigorous Coverage Gap Analysis using these inputs, producing a detailed audit and remediation report."
        
        return self.chat(prompt)
