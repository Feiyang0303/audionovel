from typing import Dict, List, Optional
import os
from pathlib import Path
import json
import ollama
from tqdm import tqdm

class TextProcessor:
    def __init__(self):
        # Define the expert roles and their prompts
        self.expert_roles = {
            "subject_researcher": {
                "role": "Subject Researcher",
                "prompt": """Analyze the text and identify:
                1. Key themes and concepts
                2. Challenging vocabulary
                3. Complex ideas that need simplification
                4. Cultural or historical references that might need explanation
                Provide a structured analysis with specific recommendations for simplification."""
            },
            "subject_reviewer": {
                "role": "Subject Reviewer",
                "prompt": """Review the identified themes and concepts:
                1. Verify accuracy of interpretations
                2. Suggest age-appropriate alternatives
                3. Identify any misconceptions
                4. Recommend additional context where needed
                Provide a detailed review with specific suggestions."""
            },
            "case_analyst": {
                "role": "Case Analyst",
                "prompt": """Break down the story into its components:
                1. Setting and environment
                2. Main characters and their roles
                3. Key plot points
                4. Conflict and resolution
                5. Character development
                Identify any complex scenarios that need simplification."""
            },
            "argument_analyzer": {
                "role": "Argument Analyzer",
                "prompt": """Analyze the logical structure:
                1. Main arguments or messages
                2. Supporting points
                3. Cause and effect relationships
                4. Complex reasoning that needs simplification
                Provide suggestions for making the logic more accessible."""
            },
            "development_analyst": {
                "role": "Development Analyst",
                "prompt": """Assess developmental appropriateness:
                1. Age-appropriate content
                2. Emotional complexity
                3. Cognitive demands
                4. Social and moral lessons
                Provide recommendations for making the content suitable for the target age group."""
            },
            "content_aggregator": {
                "role": "Content Aggregator",
                "prompt": """Compile and synthesize all expert analyses:
                1. Create a comprehensive overview
                2. Identify common themes
                3. Highlight key simplification needs
                4. Prioritize recommendations
                Provide a clear, structured summary of all expert inputs."""
            },
            "content_moderator": {
                "role": "Content Moderator",
                "prompt": """Review for appropriateness:
                1. Identify potentially sensitive content
                2. Suggest appropriate modifications
                3. Ensure cultural sensitivity
                4. Check for any problematic themes
                Provide specific recommendations for content moderation."""
            },
            "spoken_language_expert": {
                "role": "Spoken Language Expert",
                "prompt": """Analyze language patterns:
                1. Natural speech patterns
                2. Dialogue effectiveness
                3. Conversational flow
                4. Engagement level
                Suggest improvements for more engaging and natural dialogue."""
            },
            "proofreader": {
                "role": "Proofreader",
                "prompt": """Review for clarity and correctness:
                1. Grammar and punctuation
                2. Sentence structure
                3. Clarity of expression
                4. Consistency in style
                Provide specific suggestions for improvement."""
            },
            "editor": {
                "role": "Editor",
                "prompt": """Make final adjustments:
                1. Overall flow and pacing
                2. Character voice consistency
                3. Narrative engagement
                4. Age-appropriate language
                Provide final recommendations for the complete text."""
            }
        }

    def process_text(self, text: str, target_age_group: str = "8-12") -> Dict:
        """
        Process the text through all expert roles and generate a simplified version using Qwen.
        """
        results = {}
        analysis_steps = []

        # Step 1: Initial analysis by all experts
        for role_id, role_info in tqdm(self.expert_roles.items(), desc="Expert Analysis"):
            system_prompt = f"""You are a {role_info['role']} specializing in children's literature. Your task is to analyze the following text for children aged {target_age_group}.

            {role_info['prompt']}

            Provide your analysis in a clear, structured format. Focus on making the content accessible and engaging for children."""

            try:
                response = ollama.generate(
                    model="qwen2.5:32b-instruct",
                    prompt=text,
                    system=system_prompt,
                    keep_alive='1h',
                    options={"num_ctx": 30720}
                )
                
                analysis = response['response']
                results[role_id] = analysis
                analysis_steps.append({
                    "role": role_info['role'],
                    "analysis": analysis
                })
            except Exception as e:
                print(f"Error in {role_id} analysis: {str(e)}")
                results[role_id] = f"Error: {str(e)}"

        # Step 2: Generate simplified version with character dialogue
        simplification_system_prompt = f"""Based on the expert analyses, create a simplified version of the text that is appropriate for children aged {target_age_group}.

        Create a simplified version that:
        1. Maintains the original story and message
        2. Uses age-appropriate language
        3. Includes clear dialogue attribution for all characters
        4. Is engaging and easy to follow
        5. Preserves key themes and lessons

        Format the output with clear speaker attributions (e.g., "NARRATOR:", "CHARACTER_NAME:") and include:
        - A narrator for descriptive passages
        - Distinct character voices for dialogue
        - Clear scene transitions
        - Emotional expressions and reactions
        - Age-appropriate descriptions

        Expert Analyses:
        {json.dumps(analysis_steps, indent=2)}"""

        try:
            response = ollama.generate(
                model="qwen2.5:32b-instruct",
                prompt=text,
                system=simplification_system_prompt,
                keep_alive='1h',
                options={"num_ctx": 30720}
            )
            
            simplified_text = response['response']
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