from typing import Dict, List, Any
import requests
import os
from pathlib import Path
import json
from tqdm import tqdm
from dotenv import load_dotenv
import time
from datetime import datetime
import re

load_dotenv()

def get_client():
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        raise ValueError("QWEN_API_KEY not found in environment variables")
    return {
        "api_key": api_key,
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    }

client = get_client()
class TextProcessor:
    def __init__(self):
        # Define the expert roles and their prompts
        self.expert_roles = {
            "subject_researcher": {
                "role": "Subject Researcher",
                "prompt": """Analyze the text and identify:\n1. Key themes and concepts\n2. Challenging vocabulary\n3. Complex ideas that need simplification\n4. Cultural or historical references that might need explanation\nProvide a structured analysis with specific recommendations for simplification."""
            },
            "subject_reviewer": {
                "role": "Subject Reviewer",
                "prompt": """Review the identified themes and concepts:\n1. Verify accuracy of interpretations\n2. Suggest age-appropriate alternatives\n3. Identify any misconceptions\n4. Recommend additional context where needed\nProvide a detailed review with specific suggestions."""
            },
            "case_analyst": {
                "role": "Case Analyst",
                "prompt": """Break down the story into its components:\n1. Setting and environment\n2. Main characters and their roles\n3. Key plot points\n4. Conflict and resolution\n5. Character development\nIdentify any complex scenarios that need simplification."""
            },
            "argument_analyzer": {
                "role": "Argument Analyzer",
                "prompt": """Analyze the logical structure:\n1. Main arguments or messages\n2. Supporting points\n3. Cause and effect relationships\n4. Complex reasoning that needs simplification\nProvide suggestions for making the logic more accessible."""
            },
            "development_analyst": {
                "role": "Development Analyst",
                "prompt": """Assess developmental appropriateness:\n1. Age-appropriate content\n2. Emotional complexity\n3. Cognitive demands\n4. Social and moral lessons\nProvide recommendations for making the content suitable for the target age group."""
            },
            "content_aggregator": {
                "role": "Content Aggregator",
                "prompt": """Compile and synthesize all expert analyses:\n1. Create a comprehensive overview\n2. Identify common themes\n3. Highlight key simplification needs\n4. Prioritize recommendations\nProvide a clear, structured summary of all expert inputs."""
            },
            "content_moderator": {
                "role": "Content Moderator",
                "prompt": """Review for appropriateness:\n1. Identify potentially sensitive content\n2. Suggest appropriate modifications\n3. Ensure cultural sensitivity\n4. Check for any problematic themes\nProvide specific recommendations for content moderation."""
            },
            "spoken_language_expert": {
                "role": "Spoken Language Expert",
                "prompt": """Analyze language patterns:\n1. Natural speech patterns\n2. Dialogue effectiveness\n3. Conversational flow\n4. Engagement level\nSuggest improvements for more engaging and natural dialogue."""
            },
            "proofreader": {
                "role": "Proofreader",
                "prompt": """Review for clarity and correctness:\n1. Grammar and punctuation\n2. Sentence structure\n3. Clarity of expression\n4. Consistency in style\nProvide specific suggestions for improvement."""
            },
            "editor": {
                "role": "Editor",
                "prompt": """Make final adjustments:\n1. Overall flow and pacing\n2. Character voice consistency\n3. Narrative engagement\n4. Age-appropriate language\nProvide final recommendations for the complete text."""
            }
        }

    def process_text(self, text: str, target_age_group: str = "8-12", progress_callback=None) -> Dict:
        """
        Process the text through all expert roles and generate a simplified version using Qwen.
        """
        results = {}
        analysis_steps = []

        # Step 1: Initial analysis by all experts
        for role_id, role_info in tqdm(self.expert_roles.items(), desc="Expert Analysis"):
            print(f"Processing role: {role_info['role']}")
            system_prompt = f"""You are a {role_info['role']} specializing in children's literature. Your task is to analyze the following text for children aged {target_age_group}.\n\n{role_info['prompt']}\n\nProvide your analysis in a clear, structured format. Focus on making the content accessible and engaging for children."""

            try:
                response_json = self._make_api_request(
                    model="qwen-plus",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": text}
                    ]
                )
                analysis = response_json["choices"][0]["message"]["content"]
                results[role_id] = analysis
                step = {
                    "role": role_info['role'],
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
                analysis_steps.append({
                    "role": role_info['role'],
                    "analysis": analysis
                })
                if progress_callback:
                    progress_callback(step)
            except Exception as e:
                print(f"Error in {role_id} analysis: {str(e)}")
                results[role_id] = f"Error: {str(e)}"
                step = {
                    "role": role_info['role'],
                    "status": f"error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
                if progress_callback:
                    progress_callback(step)

        # Step 2: Generate simplified version with character dialogue
        simplification_system_prompt = f"""Based on the expert analyses, create a simplified version of the text that is appropriate for children aged {target_age_group}.\n\nCreate a simplified version that:\n1. Maintains the original story and message\n2. Uses age-appropriate language\n3. Includes clear dialogue attribution for all characters\n4. Is engaging and easy to follow\n5. Preserves key themes and lessons\n\nFormat the output with clear speaker attributions (e.g., \"NARRATOR:\", \"CHARACTER_NAME:\") and include:\n- A narrator for descriptive passages\n- Distinct character voices for dialogue\n- Clear scene transitions\n- Emotional expressions and reactions\n- Age-appropriate descriptions\n\nExpert Analyses:\n{json.dumps(analysis_steps, indent=2)}"""

        try:
            response_json = self._make_api_request(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": simplification_system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            simplified_text = response_json["choices"][0]["message"]["content"]
            results['simplified_text'] = simplified_text
            # Extract character information
            characters = self.extract_characters(simplified_text)
            return {
                "status": "success",
                "analysis": results,
                "simplified_text": simplified_text,
                "characters": characters,
                "target_age_group": target_age_group
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error in simplification: {str(e)}",
                "analysis": results
            }

    def extract_characters(self, simplified_text: str) -> List[Dict]:
        """
        Extract character information from the simplified text.
        Returns a list of dictionaries containing character details.
        """
        lines = simplified_text.split('\n')
        characters = {}
        for line in lines:
            if ':' in line:
                character = line.split(':', 1)[0].strip()
                dialogue = line.split(':', 1)[1].strip()
                if character != "NARRATOR":
                    if character not in characters:
                        characters[character] = {
                            "name": character,
                            "dialogue_count": 1,
                            "sample_dialogue": dialogue,
                            "first_appearance": len(characters) + 1
                        }
                    else:
                        characters[character]["dialogue_count"] += 1
        return list(characters.values())

    def _make_api_request(self, model: str, messages: List[Dict[str, str]]) -> Dict:
        """
        Make an API request to Qwen.
        """
        api_key = client["api_key"]
        base_url = client["base_url"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "messages": messages
        }
        response = requests.post(f"{base_url}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json() 