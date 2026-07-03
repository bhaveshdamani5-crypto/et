import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CrisisParserAgent:
    """
    Agent 0: Crisis Parser — The Gateway
    Transforms natural language user input into structured crisis parameters.
    """
    def __init__(self):
        self.nvidia_api_key = "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"
        if self.nvidia_api_key:
            self.llm = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.nvidia_api_key,
                timeout=10.0
            )
        else:
            self.llm = None
            
    async def parse_crisis(self, user_input: str) -> dict:
        print(f"--- PARSER AGENT: Extracting parameters for '{user_input}' ---")
        if not self.llm:
            return {
                "commodity": "unknown",
                "affected_region": "Global",
                "crisis_type": "supply_disruption",
                "search_query": user_input
            }
            
        prompt = f"""
        You are an expert energy crisis analyst. Parse the user description into structured data.
        You MUST extract ALL fields. Use your best judgment if information is implied.

        USER INPUT: "{user_input}"

        Extract these fields. NEVER return "None" or "unspecified":
        {{
            "commodity": "<crude_oil|LNG|natural_gas|thermal_coal|uranium|other>",
            "affected_country": "<specific country name>",
            "affected_region": "<continent or sub-region>",
            "volume_needed": "<Amount and unit, e.g. '50 bcm' or 'flexible'>",
            "budget_usd": "<Estimated budget in USD as a number, or 0>",
            "timeline_months": <integer months, or 1>,
            "crisis_type": "<geopolitical_tension|supply_disruption|shipping_disruption|security_threat|infrastructure_shortage|natural_disaster>",
            "severity_estimate": "<low|medium|high|critical>",
            "search_query": "<A concise 3-4 word search query for Google News regarding this crisis>"
        }}
        
        If user mentions "oil" → commodity: crude_oil
        If user mentions "gas" → commodity: natural_gas or LNG
        If user mentions "urgent/immediately" → severity_estimate: critical

        Return ONLY the raw JSON object. Do not include markdown code blocks.
        """
        
        try:
            completion = self.llm.chat.completions.create(
                model="mistralai/mistral-large-3-675b-instruct-2512",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=300
            )
            
            content = completion.choices[0].message.content
            content = content.replace("```json", "").replace("```", "").strip()
            params = json.loads(content)
            print(f"Parsed Parameters: {json.dumps(params, indent=2)}")
            return params
            
        except Exception as e:
            print(f"Error in ParserAgent: {e}")
            return {
                "commodity": "unknown",
                "affected_region": "unknown",
                "crisis_type": "unknown",
                "search_query": user_input
            }
