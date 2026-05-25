import os
import logging
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str, api_key: str = None, model: str = "gpt-4o"):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model = model
        # Check for Groq API key first, then fall back to OpenAI
        self.api_key = api_key or os.getenv("Groq_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.use_groq = bool(os.getenv("Groq_API_KEY") or (api_key and api_key.startswith("gsk_")))
        
        # Initialize client lazily to avoid throwing errors during import
        self._client = None
        logging.info(f"Agent '{self.name}' ({self.role}) initialized with model: {self.model} (Groq: {self.use_groq})")

    @property
    def client(self):
        """Lazy-initialize OpenAI/Groq client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    f"API Key is missing for agent '{self.name}'. "
                    "Please set the Groq_API_KEY or OPENAI_API_KEY environment variable."
                )
            if self.use_groq:
                # Use Groq API endpoint
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            else:
                # Use OpenAI API endpoint
                self._client = OpenAI(api_key=self.api_key)
        return self._client

    def chat(self, prompt: str, temperature: float = 0.2) -> str:
        """Sends a query to OpenAI using the agent's defined role, system prompt, and context."""
        logging.info(f"Agent '{self.name}' is thinking...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            reply = response.choices[0].message.content.strip()
            logging.info(f"Agent '{self.name}' finished thinking.")
            return reply
        except Exception as e:
            error_msg = f"Agent '{self.name}' encountered LLM communication error: {str(e)}"
            logging.error(error_msg)
            return f"ERROR: Could not get a response from the model. Details: {str(e)}"

    def collaborate(self, recipient_agent, prompt: str) -> str:
        """Demonstrates agent collaboration: this agent prepares structured prompt request and passes it to another."""
        logging.info(f"Collaboration: Agent '{self.name}' is handing off task to '{recipient_agent.name}'")
        handoff_prompt = f"Handoff from {self.name} ({self.role}):\n\n{prompt}"
        return recipient_agent.chat(handoff_prompt)
