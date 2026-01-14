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
from threading import Thread
from flask import jsonify

load_dotenv()

def _is_trivial_short_text(text: str) -> bool:
    """Heuristic: treat very short inputs as trivial to avoid over-generation."""
    if not text:
        return True
    stripped = text.strip()
    if len(stripped) <= 60:
        return True
    words = stripped.split()
    return len(words) <= 12

def _create_minimal_script_from_text(text: str) -> str:
    """Return a single grounded line with no invented content."""
    content = text.strip()
    if not content:
        return "NARRATOR: "
    # Capitalize first letter if needed and ensure terminal punctuation
    normalized = content[0].upper() + content[1:] if content else content
    if normalized[-1] not in ".!?":
        normalized += "."
    return f"NARRATOR: {normalized}"

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
        # Short-input minimal mode to avoid making things up
        if _is_trivial_short_text(text):
            simplified_text = _create_minimal_script_from_text(text)
            characters = self.extract_characters(simplified_text)
            return {
                "status": "success",
                "analysis": {"mode": "minimal_short_input"},
                "simplified_text": simplified_text,
                "characters": characters,
                "target_age_group": target_age_group
            }

        results = {}
        analysis_steps = []

        # Check if API key is available
        api_key = os.getenv("QWEN_API_KEY")
        if not api_key:
            # Fallback: Create a simple simplified version without AI processing
            print("QWEN_API_KEY not found. Using fallback processing.")
            simplified_text = self._create_fallback_simplified_text(text, target_age_group)
            characters = self.extract_characters(simplified_text)
            return {
                "status": "success",
                "analysis": {"fallback": "AI service not available - using basic processing"},
                "simplified_text": simplified_text,
                "characters": characters,
                "target_age_group": target_age_group
            }

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
                # Continue with fallback for this role
                results[role_id] = f"Error: {str(e)}"
                step = {
                    "role": role_info['role'],
                    "status": f"error: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
                if progress_callback:
                    progress_callback(step)

        # Step 2: Generate simplified version with character dialogue
        try:
            simplification_system_prompt = f"""Based on the expert analyses, create a simplified version of the text that is appropriate for children aged {target_age_group}.\n\nCreate a simplified version that:\n1. Maintains the original story and message\n2. Uses age-appropriate language\n3. Includes clear speaker attributions like \"NARRATOR:\" and \"CHARACTER_NAME:\"\n4. Is engaging and easy to follow\n5. Preserves key themes and lessons\n\nStrict grounding constraints:\n- Do NOT invent story elements, characters, scenes, or facts that are not present in the input text.\n- Keep output length roughly proportional to the input length. For short inputs (≈1–2 sentences), produce at most 1–2 lines.\n- If the input is extremely short or generic, return a single grounded line (e.g., 'NARRATOR: <original>') with minimal formatting.\n\nElevenLabs tag rules:\n- Use ONLY these voice tags inline (square brackets), when contextually appropriate:\n  [happy], [sad], [excited], [angry], [whisper], [annoyed], [appalled], [thoughtful], [surprised],\n  [laughing], [chuckles], [sighs], [clears throat], [short pause], [long pause], [exhales sharply], [inhales deeply],\n  and common variants like [whispers], [laughs], [crying], [sarcastic], [curious].\n- Do NOT use any environmental SFX or non-voice actions (e.g., [applause], [explosion], [music], [footsteps]). Voice-only.\n- Use tags sparingly (no more than 1–2 per sentence) and only when they enhance the line.\n- Punctuation shapes delivery: ellipses (…) add pauses; capitalization adds emphasis; standard punctuation drives rhythm.\n\nExpert Analyses:\n{json.dumps(analysis_steps, indent=2)}"""

            response_json = self._make_api_request(
                model="qwen-plus",
                messages=[
                    {"role": "system", "content": simplification_system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            simplified_text = response_json["choices"][0]["message"]["content"]
            results['simplified_text'] = simplified_text
        except Exception as e:
            print(f"Error in AI simplification: {str(e)}. Using fallback processing.")
            # Use fallback if AI simplification fails
            simplified_text = self._create_fallback_simplified_text(text, target_age_group)
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

    def _create_fallback_simplified_text(self, text: str, target_age_group: str) -> str:
        """
        Create a simplified version of the text without AI processing.
        """
        # Basic text processing
        lines = text.split('\n')
        simplified_lines = []
        
        # Add narrator introduction
        simplified_lines.append("NARRATOR: Once upon a time, there was a story to tell.")
        
        # Process each paragraph
        for line in lines:
            line = line.strip()
            if line:
                # Simple sentence splitting and simplification
                sentences = re.split(r'[.!?]+', line)
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence and len(sentence) > 10:
                        # Basic simplification: shorter sentences, simpler words
                        simplified_sentence = self._simplify_sentence(sentence)
                        simplified_lines.append(f"NARRATOR: {simplified_sentence}")
        
        # Add conclusion
        simplified_lines.append("NARRATOR: And that's the end of our story.")
        
        return '\n'.join(simplified_lines)
    
    def _simplify_sentence(self, sentence: str) -> str:
        """
        Basic sentence simplification.
        """
        # Remove extra whitespace
        sentence = re.sub(r'\s+', ' ', sentence)
        
        # Basic word replacement for common complex words
        replacements = {
            'subsequently': 'then',
            'nevertheless': 'but',
            'furthermore': 'also',
            'consequently': 'so',
            'approximately': 'about',
            'demonstrate': 'show',
            'utilize': 'use',
            'implement': 'use',
            'facilitate': 'help',
            'comprehensive': 'complete'
        }
        
        for complex_word, simple_word in replacements.items():
            sentence = re.sub(r'\b' + complex_word + r'\b', simple_word, sentence, flags=re.IGNORECASE)
        
        # Ensure sentence ends with punctuation
        if sentence and not sentence[-1] in '.!?':
            sentence += '.'
        
        return sentence

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