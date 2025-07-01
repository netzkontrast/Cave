import openai
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import Character, Scene, Interaction, Memory, SceneCharacter, CharacterFeeling
from .schemas import InteractionType, MemoryType
import os
from dotenv import load_dotenv

load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class AIEngine:
    def __init__(self, model="gpt-3.5-turbo"):
        self.client = openai.OpenAI()
        self.logger = logging.getLogger(__name__)
        self.model = model
    
    def set_model(self, model):
        """Set the AI model to use"""
        if model in ["gpt-4", "gpt-3.5-turbo"]:
            self.model = model
            self.logger.info(f"AI model set to: {self.model}")
        else:
            self.logger.warning(f"Invalid model: {model}. Using default: gpt-3.5-turbo")
            self.model = "gpt-3.5-turbo"
    
    def generate_character_interaction(
        self, 
        character: Character, 
        scene: Scene, 
        other_characters: List[Character],
        recent_interactions: List[Interaction],
        character_memories: List[Memory],
        max_length: int = 50
    ) -> Dict[str, Any]:
        """
        Generate an autonomous interaction for a character based on their personality,
        the scene context, and their memories of other characters.
        """
        try:
            # Build context from character's memories and relationships
            memory_context = self._build_memory_context(character, character_memories, other_characters)
            
            # Build recent interaction context
            interaction_context = self._build_interaction_context(recent_interactions)
            
            # Create the prompt
            prompt = self._create_interaction_prompt(
                character, scene, other_characters, memory_context, interaction_context, max_length
            )
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI that generates realistic character interactions for novel writing. ALWAYS include atmospheric narrative descriptions that set the scene, describe the environment, and add sensory details. Focus on natural dialogue, character development, and rich atmospheric storytelling that contributes to the plot."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length + 50,  # More conservative token allocation
                temperature=0.8
            )
            
            interaction_text = response.choices[0].message.content.strip()
            
            # Analyze the interaction for emotional content and targets
            analysis = self._analyze_interaction(interaction_text, character, other_characters)
            
            return {
                "content": interaction_text,
                "interaction_type": analysis.get("type", InteractionType.DIALOGUE),
                "emotional_state": analysis.get("emotional_state"),
                "target_character_id": analysis.get("target_character_id"),
                "character_thoughts": analysis.get("thoughts"),
                "relationship_insights": analysis.get("relationship_insights")
            }
            
        except Exception as e:
            self.logger.error(f"Error generating interaction: {e}")
            return {
                "content": f"[{character.name} remains silent, lost in thought...]",
                "interaction_type": InteractionType.THOUGHT,
                "emotional_state": "contemplative",
                "target_character_id": None,
                "character_thoughts": "The character is processing recent events...",
                "relationship_insights": {}
            }
    
    def generate_scene_narration(
        self,
        scene: Scene,
        characters: List[Character],
        recent_interactions: List[Interaction],
        narration_type: str = "atmospheric"
    ) -> str:
        """
        Generate narrative descriptions that set the scene, describe the environment,
        and add atmospheric details that contribute to the plot.
        """
        try:
            # Build context from recent interactions
            interaction_context = self._build_interaction_context(recent_interactions)
            
            prompt = f"""
Generate a narrative description for this scene that enhances the atmosphere and contributes to the plot:

SCENE DETAILS:
Title: {scene.title}
Environment: {scene.environment}
Context: {scene.context}
Weather: {scene.weather or "Not specified"}
Time: {scene.time_of_day or "Not specified"}
Mood: {scene.mood or "Not specified"}

CHARACTERS PRESENT:
{[f"- {c.name}: {c.personality[:60]}..." for c in characters]}

RECENT INTERACTIONS:
{interaction_context}

NARRATION TYPE: {narration_type}

Generate a narrative description that:
1. **Sets the atmospheric tone** - Describe the environment, lighting, sounds, smells
2. **Shows character dynamics** - How characters are positioned, their body language, subtle interactions
3. **Advances the plot** - Include details that hint at future developments or reveal character motivations
4. **Creates tension or mood** - Use sensory details to build the emotional atmosphere
5. **Provides context** - Connect to the broader story and character relationships

Keep it concise but evocative (2-3 sentences). Focus on details that matter to the story.

Narrative description:
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI that generates atmospheric narrative descriptions for novel writing. Focus on sensory details, character dynamics, and plot advancement."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,  # Reduced from 200 to 150
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"Error generating scene narration: {e}")
            return f"The scene continues with an air of {scene.mood or 'tension'} hanging in the air."
    
    def _build_memory_context(self, character: Character, memories: List[Memory], other_characters: List[Character]) -> str:
        """Build context from character's key memory points of other characters."""
        if not memories:
            return "No previous memories with these characters."
        
        memory_texts = []
        for memory in memories[-3:]:  # Reduced from 5 to 3 memories
            if memory.related_characters:
                try:
                    related_ids = json.loads(memory.related_characters)
                    related_names = [c.name for c in other_characters if c.id in related_ids]
                    if related_names:
                        # Truncate memory content for cost efficiency
                        memory_texts.append(f"Memory: {memory.key_points[:100]}... (involving: {', '.join(related_names)})")
                except json.JSONDecodeError:
                    memory_texts.append(f"Memory: {memory.key_points[:100]}...")
        
        return "Recent memories: " + "; ".join(memory_texts) if memory_texts else "No recent memories."
    
    def _build_interaction_context(self, interactions: List[Interaction]) -> str:
        """Build context from recent interactions in the scene."""
        if not interactions:
            return "No recent interactions in this scene."
        
        recent_texts = []
        for interaction in interactions[-2:]:  # Reduced from 3 to 2 interactions
            # Truncate interaction content for cost efficiency
            recent_texts.append(f"{interaction.character.name}: {interaction.content[:80]}...")
        
        return "Recent scene interactions: " + " | ".join(recent_texts)
    
    def _create_interaction_prompt(
        self, 
        character: Character, 
        scene: Scene, 
        other_characters: List[Character],
        memory_context: str,
        interaction_context: str,
        max_length: int
    ) -> str:
        """Create a detailed prompt for character interaction generation."""
        
        other_characters_info = "\n".join([
            f"- {c.name}: {c.personality[:60]}..." for c in other_characters  # Reduced from 100 to 60 chars
        ])
        
        prompt = f"""
You are {character.name}, a character in a novel. Generate a natural interaction based on the following context:

CHARACTER PROFILE:
Name: {character.name}
Personality: {character.personality}
Background: {character.background}
Goals: {character.goals or "Not specified"}
Fears: {character.fears or "Not specified"}

SCENE CONTEXT:
Title: {scene.title}
Environment: {scene.environment}
Context: {scene.context}
Weather: {scene.weather or "Not specified"}
Time: {scene.time_of_day or "Not specified"}
Mood: {scene.mood or "Not specified"}

OTHER CHARACTERS PRESENT:
{other_characters_info}

MEMORY CONTEXT:
{memory_context}

RECENT INTERACTIONS:
{interaction_context}

INSTRUCTIONS:
Generate a natural interaction that includes:
1. **Dialogue or action** - What {character.name} says or does
2. **Narrative description** - ALWAYS include atmospheric details about the scene, character movements, environmental elements, and sensory details
3. **Character voice** - Make it authentic to {character.name}'s personality
4. **Plot advancement** - Include details that move the story forward
5. **Atmospheric elements** - Reference the environment, mood, lighting, sounds, smells, or other sensory details
6. **Scene setting** - Describe the immediate surroundings and how they affect the interaction

IMPORTANT: Every interaction should include narrative elements that set the scene and create atmosphere. This is not just dialogue - it's novel writing that describes the environment, character positioning, and atmospheric details that contribute to the plot.

Keep it under {max_length} words total. The interaction should feel like a natural part of a novel scene with rich atmospheric details.

Generate the interaction:
"""
        return prompt
    
    def _analyze_interaction(self, interaction_text: str, character: Character, other_characters: List[Character]) -> Dict[str, Any]:
        """Analyze the generated interaction for emotional content and targets."""
        try:
            analysis_prompt = f"""
Analyze this character interaction and return a JSON response:

Interaction: "{interaction_text}"
Character: {character.name}
Other characters: {[c.name for c in other_characters]}

Return JSON with:
- "type": "dialogue", "thought", "action", or "narration"
- "emotional_state": brief emotional description
- "target_character_id": ID of character being addressed (if any)
- "thoughts": internal thoughts if this is a thought
- "relationship_insights": brief insights about character relationships
- "narrative_elements": atmospheric or environmental details included

JSON response:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI that analyzes character interactions. Return only valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=150,  # Reduced from 200 to 150
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content.strip()
            analysis = json.loads(analysis_text)
            
            # Find target character ID if name is provided
            if analysis.get("target_character_id"):
                if isinstance(analysis["target_character_id"], str):
                    target_name = analysis["target_character_id"]
                    target_char = next((c for c in other_characters if c.name.lower() in target_name.lower()), None)
                    if target_char:
                        analysis["target_character_id"] = target_char.id
                    else:
                        analysis["target_character_id"] = None
                elif isinstance(analysis["target_character_id"], list):
                    # If it's a list, take the first character name and convert to ID
                    if analysis["target_character_id"]:
                        target_name = analysis["target_character_id"][0]
                        target_char = next((c for c in other_characters if c.name.lower() in target_name.lower()), None)
                        if target_char:
                            analysis["target_character_id"] = target_char.id
                        else:
                            analysis["target_character_id"] = None
                    else:
                        analysis["target_character_id"] = None
                else:
                    analysis["target_character_id"] = None
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing interaction: {e}")
            return {
                "type": InteractionType.DIALOGUE,
                "emotional_state": "neutral",
                "target_character_id": None,
                "thoughts": None,
                "relationship_insights": {}
            }
    
    def generate_memory_from_interaction(
        self, 
        character: Character, 
        interaction: Interaction, 
        scene: Scene,
        other_characters: List[Character]
    ) -> Optional[Memory]:
        """Generate key bullet points for a character's memory based on an interaction."""
        try:
            prompt = f"""
Based on this interaction, generate key bullet points that {character.name} would remember:

Interaction: "{interaction.content}"
Type: {interaction.interaction_type}
Emotional State: {interaction.emotional_state or "neutral"}
Scene: {scene.title} - {scene.context}

Other characters present: {[c.name for c in other_characters]}

Generate 3-5 key bullet points that {character.name} would remember from this interaction. Focus on:
- Important information revealed
- Character behavior or personality traits observed
- Emotional reactions or feelings
- Any revelations or insights
- Atmospheric or environmental details that affected them

Format as bullet points, keep each point concise and memorable.

Return JSON with:
- "key_points": the bullet points (as a single string with line breaks)
- "memory_type": "interaction", "observation", "feeling", or "revelation"
- "emotional_impact": number from -100 to 100
- "related_characters": list of character IDs involved
- "importance": number from 1-5 (how important this memory is)

JSON response:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI that generates character memories as key bullet points. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,  # Reduced from 300 to 200
                temperature=0.7
            )
            
            memory_data = json.loads(response.choices[0].message.content.strip())
            
            # Find related character IDs
            related_ids = []
            if memory_data.get("related_characters"):
                for char_name in memory_data["related_characters"]:
                    char = next((c for c in other_characters if c.name.lower() in char_name.lower()), None)
                    if char:
                        related_ids.append(char.id)
            
            return Memory(
                character_id=character.id,
                key_points=memory_data["key_points"],
                memory_type=memory_data["memory_type"],
                emotional_impact=memory_data["emotional_impact"],
                related_characters=json.dumps(related_ids),
                scene_id=scene.id,
                importance=memory_data.get("importance", 1)
            )
            
        except Exception as e:
            self.logger.error(f"Error generating memory: {e}")
            return None
    
    def update_character_feelings(
        self,
        character: Character,
        interaction: Interaction,
        other_characters: List[Character]
    ) -> List[CharacterFeeling]:
        """Update character feelings about other characters based on an interaction."""
        try:
            prompt = f"""
Based on this interaction, analyze how {character.name} feels about other characters:

Interaction: "{interaction.content}"
Character: {character.name}
Emotional State: {interaction.emotional_state or "neutral"}

Other characters present: {[c.name for c in other_characters]}

Analyze how this interaction affects {character.name}'s feelings about each other character present.
Consider their personality, goals, and the nature of the interaction.

Return JSON with an array of feeling updates:
- "target_character_id": ID of the character they feel about
- "feeling_type": "trust", "distrust", "affection", "anger", "respect", "fear", "curiosity", etc.
- "intensity": number from -100 to 100 (negative = negative feeling, positive = positive feeling)
- "reason": brief reason for the feeling change

JSON response:
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI that analyzes character feelings. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,  # Reduced from 400 to 250
                temperature=0.7
            )
            
            feelings_data = json.loads(response.choices[0].message.content.strip())
            
            # Ensure feelings_data is a list
            if not isinstance(feelings_data, list):
                self.logger.warning(f"Expected list for feelings_data, got {type(feelings_data)}: {feelings_data}")
                return []
            
            feelings = []
            for feeling_data in feelings_data:
                # Ensure feeling_data is a dictionary
                if not isinstance(feeling_data, dict):
                    self.logger.warning(f"Expected dict for feeling_data, got {type(feeling_data)}: {feeling_data}")
                    continue
                
                # Find target character ID if name is provided
                target_char = None
                if isinstance(feeling_data.get("target_character_id"), str):
                    target_name = feeling_data["target_character_id"]
                    target_char = next((c for c in other_characters if c.name.lower() in target_name.lower()), None)
                
                if target_char:
                    feeling = CharacterFeeling(
                        character_id=character.id,
                        target_character_id=target_char.id,
                        feeling_type=feeling_data["feeling_type"],
                        intensity=feeling_data["intensity"],
                        reason=feeling_data.get("reason", "")
                    )
                    feelings.append(feeling)
            
            return feelings
            
        except Exception as e:
            self.logger.error(f"Error updating character feelings: {e}")
            return []
    
    def analyze_character_relationships(
        self, 
        character: Character, 
        other_characters: List[Character],
        interactions: List[Interaction],
        memories: List[Memory]
    ) -> Dict[str, Any]:
        """Analyze and suggest relationship developments between characters."""
        try:
            # Get interactions involving this character
            char_interactions = [i for i in interactions if i.character_id == character.id or i.target_character_id == character.id]
            
            prompt = f"""
Analyze the relationships between {character.name} and other characters based on their interactions and memories.

Character: {character.name}
Personality: {character.personality}

Other characters: {[c.name for c in other_characters]}

Recent interactions: {[f"{i.content[:50]}..." for i in char_interactions[-5:]]}
Recent memories: {[m.key_points[:50] + "..." for m in memories[-5:]]}

Analyze and suggest:
1. Current relationship status with each character
2. Potential relationship developments
3. Character dynamics and conflicts
4. Writing inspiration for relationship arcs

Return JSON with relationship insights.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI that analyzes character relationships for novel writing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"Error analyzing relationships: {e}")
            return {"error": "Could not analyze relationships"}
    
    def generate_plot_inspiration(
        self, 
        scene: Scene, 
        characters: List[Character],
        interactions: List[Interaction]
    ) -> List[str]:
        """Generate plot inspiration based on scene interactions."""
        try:
            prompt = f"""
Based on this scene and character interactions, generate plot inspiration for novel writing:

Scene: {scene.title}
Context: {scene.context}
Characters: {[c.name for c in characters]}

Recent interactions: {[f"{i.character.name}: {i.content[:100]}..." for i in interactions[-10:]]}

Generate 5 plot points or story developments that could emerge from these interactions.
Focus on character development, conflicts, and story progression.

Return as a JSON array of strings.
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an AI that generates plot inspiration for novel writing."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.8
            )
            
            return json.loads(response.choices[0].message.content.strip())
            
        except Exception as e:
            self.logger.error(f"Error generating plot inspiration: {e}")
            return ["Continue developing character relationships", "Explore character backstories", "Introduce new conflicts"]
    
    def generate_unified_scene_conversation(
        self,
        scene: Scene,
        characters: List[Character],
        max_length: int = 100,
        previous_interactions: List[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Generate a unified scene conversation where all characters interact together naturally."""
        try:
            # Build character context (minimal)
            character_names = [char.name for char in characters]
            
            # Build conversation context if continuing
            conversation_context = ""
            if previous_interactions:
                recent_dialogue = []
                for interaction in previous_interactions[-5:]:  # Last 5 interactions for better context
                    recent_dialogue.append(f"{interaction['character_name']}: {interaction['content']}")
                conversation_context = f"\n\nRECENT DIALOGUE:\n" + "\n".join(recent_dialogue)
            
            # Determine conversation length based on context
            if previous_interactions and len(previous_interactions) > 10:
                # Later in conversation: 2-4 exchanges, more focused
                num_exchanges = "2-4"
                focus = "Continue the plot development and character relationships. Don't repeat introductions."
            else:
                # Early in conversation: 3-5 exchanges, more setup
                num_exchanges = "3-5"
                focus = "Develop the scene and establish character dynamics naturally."
            
            prompt = f"""Scene: {scene.title} - {scene.context}
Environment: {scene.environment}
Characters: {', '.join(character_names)}

{conversation_context}

Write {num_exchanges} natural interactions that advance the plot and develop character relationships.

IMPORTANT RULES:
- NO introductions or "Hello, I'm [Name]" - characters already know each other
- Vary who speaks - not everyone needs to speak in every round
- Focus on the mystery/plot: {scene.context}
- Make dialogue natural and character-specific
- Include reactions, questions, plans, revelations
- Build on previous dialogue, don't repeat

NARRATIVE WRITING STYLE:
You are writing a novel scene, not just dialogue. Each interaction should include:
- Character actions and movements (e.g., "Emma leaned forward, her eyes narrowing")
- Environmental descriptions (e.g., "The diner's neon sign flickered outside")
- Atmospheric details (e.g., "The air grew tense as Marcus spoke")
- Character expressions and body language (e.g., "Sarah's hands trembled as she spoke")
- Scene transitions and pacing
- Sensory details (sounds, smells, lighting, temperature)

FORMAT EXAMPLES:
- Pure narrative: "The old floorboards creaked as Detective Martinez paced the room, his shadow dancing on the peeling wallpaper."
- Action + dialogue: "Emma slammed her coffee cup down, the sound echoing through the empty diner. 'What do you mean by that?'"
- Narrative + dialogue: "The diner fell silent except for the hum of the refrigerator. Outside, rain began to patter against the windows. 'What do you mean by that?' Emma finally asked, her voice barely above a whisper."
- Environmental focus: "The flickering fluorescent light cast strange shadows across the table, making the coffee stains look like dark secrets spilled across the surface."

You can write interactions that are purely narrative (describing the environment, character actions, or atmospheric details) without any dialogue. This creates rich, novel-like scenes.

Return JSON:
[
  {{"character_name": "Name", "content": "What they say or do", "interaction_type": "dialogue/thought/action/narration", "emotional_state": "feeling", "target_character_id": "who they're talking to"}}
]"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a novelist writing rich, atmospheric scenes. Create natural, plot-driven interactions that include dialogue, character actions, environmental descriptions, and atmospheric details. Write like a novel, not just dialogue. NO introductions. Vary speakers and include narrative elements. Use ONLY these interaction_type values: 'dialogue', 'thought', 'action', 'narration'."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,  # Increased from 400 to 800 for richer narrative content
                temperature=0.8  # Slightly higher for more variety
            )
            
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON if there's extra text
            try:
                # Look for JSON array in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                if start_idx != -1 and end_idx != 0:
                    json_content = content[start_idx:end_idx]
                    # Try to fix common JSON issues
                    json_content = json_content.replace('\n', ' ').replace('\r', ' ')
                    # Remove any trailing incomplete objects
                    if json_content.count('{') > json_content.count('}'):
                        # Find the last complete object
                        last_complete = json_content.rfind('},')
                        if last_complete != -1:
                            json_content = json_content[:last_complete+1] + ']'
                        else:
                            # If no complete objects, try to close the last one
                            json_content = json_content.rstrip(',') + '}]'
                    
                    conversation_data = json.loads(json_content)
                else:
                    conversation_data = json.loads(content)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parsing error: {e}")
                self.logger.error(f"Raw response: {content}")
                # Try to extract partial data
                try:
                    # Look for individual JSON objects
                    import re
                    json_objects = re.findall(r'\{[^{}]*\}', content)
                    conversation_data = []
                    for obj_str in json_objects:
                        try:
                            obj = json.loads(obj_str)
                            if 'character_name' in obj and 'content' in obj:
                                conversation_data.append(obj)
                        except:
                            continue
                except:
                    conversation_data = []
                
                # If still no data, create fallback
                if not conversation_data and characters:
                    # Create one focused interaction about the plot with narrative
                    main_char = characters[0]
                    conversation_data.append({
                        "character_name": main_char.name,
                        "content": f"{main_char.name} leaned forward, her eyes gleaming with determination. 'We need to figure out what really happened with that missing hiker.'",
                        "interaction_type": "dialogue",
                        "emotional_state": "determined",
                        "target_character_id": None
                    })
            
            # Convert to the expected format and find character IDs
            interactions = []
            for interaction_data in conversation_data:
                # Find character by name
                character = next((c for c in characters if c.name.lower() in interaction_data["character_name"].lower()), None)
                if not character:
                    continue
                
                # Find target character if specified
                target_character = None
                if interaction_data.get("target_character_id"):
                    target_name = interaction_data["target_character_id"]
                    target_character = next((c for c in characters if c.name.lower() in target_name.lower()), None)
                
                # Validate and fix interaction_type
                interaction_type = interaction_data.get("interaction_type", "dialogue")
                if interaction_type not in ["dialogue", "thought", "action", "narration"]:
                    # Convert common incorrect values
                    if interaction_type in ["narrative", "description", "environmental"]:
                        interaction_type = "narration"
                    elif interaction_type in ["movement", "gesture", "physical"]:
                        interaction_type = "action"
                    else:
                        interaction_type = "dialogue"  # Default fallback
                
                interactions.append({
                    "character_name": character.name,
                    "content": interaction_data["content"],
                    "interaction_type": interaction_type,
                    "emotional_state": interaction_data["emotional_state"],
                    "target_character_id": target_character.id if target_character else None
                })
            
            return interactions
            
        except Exception as e:
            self.logger.error(f"Error generating unified scene conversation: {e}")
            # Return fallback interactions focused on plot with narrative
            fallback_interactions = []
            if characters:
                fallback_interactions.append({
                    "character_name": characters[0].name,
                    "content": f"{characters[0].name} glanced around the {scene.environment.lower()}, her curiosity piqued. 'We should investigate this mystery further.'",
                    "interaction_type": "dialogue",
                    "emotional_state": "curious",
                    "target_character_id": None
                })
            return fallback_interactions 