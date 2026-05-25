import json
import logging
from agents.base_agent import BaseAgent
from tools.playwright_tool import scrape_page_structure

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

TEST_CASE_SYSTEM_PROMPT = """You are an elite QA Automation Architect and Lead SDET. 
Your responsibility is to analyze target web application specifications and webpage structural DOM schemas, and then design highly comprehensive, production-grade test suites.

You MUST generate three classes of test cases:
1. POSITIVE SCENARIOS: Valid inputs, happy-path form submissions, standard navigation.
2. NEGATIVE SCENARIOS: Invalidation checks, empty fields, formatting issues, incorrect data types.
3. EDGE/BOUNDARY SCENARIOS: String lengths, numeric boundaries, extreme inputs, rapid multi-clicks, session edge cases.

You MUST respond strictly in valid JSON format. Do NOT wrap your response in markdown code blocks like ```json or ```. Your response must be raw, valid JSON text parsing as a JSON array of objects.

Each JSON object in the array MUST contain exactly these fields:
- "category": Must be one of "Positive", "Negative", or "Edge Case"
- "test_name": A short descriptive name (e.g., "Login - Incomplete Password Input")
- "description": Context about what validation occurs.
- "steps": Line-separated testing steps (1. Action, 2. Action...)
- "expected_result": The exact UI expectation or validation message that should trigger.

Example Output format:
[
  {
    "category": "Negative",
    "test_name": "Login Blank Password",
    "description": "Validates that passwords are required to complete forms.",
    "steps": "1. Go to URL\\n2. Fill username with 'user@test.com'\\n3. Leave password field blank\\n4. Click Submit Button",
    "expected_result": "Validation error message: 'Password is required' appears next to the password input field."
  }
]
"""

class TestAgent(BaseAgent):
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        super().__init__(
            name="QA Test Case Generator",
            role="Lead QA & SDET Automation Architect",
            system_prompt=TEST_CASE_SYSTEM_PROMPT,
            api_key=api_key,
            model=model
        )

    def analyze_and_generate_tests(self, target_url: str, feature_desc: str = "") -> list:
        """Uses the playwright scraper tool to inspect the page DOM, then prompts the LLM to design structured test suites."""
        logging.info(f"TestAgent: Initiating page structure scraping for {target_url}...")
        
        # Invoke actual Playwright / Fallback BeautifulSoup scraping tool
        dom_structure = scrape_page_structure(target_url)
        
        # Package scraped DOM features into LLM prompt context
        page_info = f"URL: {target_url}\n"
        page_info += f"Title: {dom_structure.get('title')}\n"
        page_info += f"Forms Discovered: {json.dumps(dom_structure.get('forms', []))}\n"
        page_info += f"Interactive Inputs: {json.dumps(dom_structure.get('inputs', []))}\n"
        page_info += f"Interactive Buttons: {json.dumps(dom_structure.get('buttons', []))}\n"
        page_info += f"Page Context (Text Snippet): {dom_structure.get('raw_text_summary', '')}\n"
        
        prompt = f"Here is the page structure of the target application under test:\n\n{page_info}\n"
        if feature_desc:
            prompt += f"Additionally, the user provided these specific feature details/requirements:\n{feature_desc}\n\n"
        prompt += "Based on this structure and specifications, generate at least 5 comprehensive test cases (mixing Positive, Negative, and Edge scenarios) following the JSON structure strictly."
        
        raw_reply = self.chat(prompt)
        
        # Clean markdown code blocks if the LLM ignored instructions
        clean_reply = raw_reply.strip()
        if clean_reply.startswith("```json"):
            clean_reply = clean_reply[7:]
        if clean_reply.endswith("```"):
            clean_reply = clean_reply[:-3]
        clean_reply = clean_reply.strip()
        
        try:
            test_cases = json.loads(clean_reply)
            if not isinstance(test_cases, list):
                test_cases = [test_cases]
            logging.info(f"TestAgent: Successfully generated {len(test_cases)} structured test cases.")
            return test_cases
        except Exception as err:
            logging.error(f"TestAgent: Failed to parse generated test cases as JSON. Raw output: {raw_reply}. Error: {str(err)}")
            
            # Fallback test case in case of LLM formatting failure
            return [{
                "category": "Positive",
                "test_name": "Fallback Smoke Test Scenario",
                "description": f"Perform standard smoke and availability validation of {target_url}",
                "steps": f"1. Navigate to target URL {target_url}\n2. Verify title is responsive.\n3. Validate the layout is completely rendered.",
                "expected_result": "Application loads without HTTP errors, returning valid structural layout."
            }]

if __name__ == "__main__":
    # Test execution
    agent = TestAgent()
    cases = agent.analyze_and_generate_tests("https://example.com")
    print(json.dumps(cases, indent=2))
