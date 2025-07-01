#!/usr/bin/env python3
"""
Interactive test script for Cave - User-driven scene creation and conversation generation
"""
import sys
import os
import requests
import json
from datetime import datetime
import time

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class CaveInteractive:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.model = "gpt-3.5-turbo"  # Default model
    
    def set_model(self, model):
        """Set the AI model to use"""
        if model in ["gpt-4", "gpt-3.5-turbo"]:
            response = self.session.post(f"{self.base_url}/ai/model", params={"model": model})
            if response.status_code == 200:
                self.model = model
                print(f"✅ Model set to: {self.model}")
            else:
                print(f"❌ Error setting model: {response.text}")
        else:
            print("❌ Invalid model. Use 'gpt-4' or 'gpt-3.5-turbo'")
    
    def get_model(self):
        """Get current model setting"""
        response = self.session.get(f"{self.base_url}/ai/model")
        if response.status_code == 200:
            data = response.json()
            self.model = data.get("current_model", "gpt-3.5-turbo")
        return self.model
    
    def check_server(self):
        """Check if the server is running"""
        try:
            response = self.session.get(f"{self.base_url}/characters/")
            return response.status_code == 200
        except:
            return False
    
    def create_character(self, name, personality, background, appearance=None, goals=None, fears=None):
        """Create a new character"""
        character_data = {
            "name": name,
            "personality": personality,
            "background": background,
            "appearance": appearance,
            "goals": goals,
            "fears": fears
        }
        
        response = self.session.post(f"{self.base_url}/characters/", json=character_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error creating character: {response.text}")
            return None
    
    def create_scene(self, title, environment, context, character_ids, weather=None, time_of_day=None, mood=None):
        """Create a new scene with characters"""
        scene_data = {
            "title": title,
            "environment": environment,
            "context": context,
            "character_ids": character_ids,
            "weather": weather,
            "time_of_day": time_of_day,
            "mood": mood
        }
        
        response = self.session.post(f"{self.base_url}/scenes/", json=scene_data)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error creating scene: {response.text}")
            return None
    
    def advance_timeline(self, scene_id):
        """Advance the scene timeline and generate interactions"""
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/timeline/advance")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error advancing timeline: {response.text}")
            return None
    
    def generate_individual_interaction(self, scene_id, character_id, max_length=50):
        """Generate interaction for a specific character"""
        response = self.session.post(
            f"{self.base_url}/scenes/{scene_id}/interactions/generate",
            params={"character_id": character_id, "max_length": max_length}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error generating interaction: {response.text}")
            return None
    
    def get_scene_timeline(self, scene_id):
        """Get the complete timeline for a scene"""
        response = self.session.get(f"{self.base_url}/scenes/{scene_id}/timeline")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting timeline: {response.text}")
            return None
    
    def summarize_scene(self, scene_id):
        """Summarize the scene events"""
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/summarize")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error summarizing scene: {response.text}")
            return None
    
    def get_characters(self):
        """Get all characters"""
        response = self.session.get(f"{self.base_url}/characters/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting characters: {response.text}")
            return []
    
    def get_scenes(self):
        """Get all scenes"""
        response = self.session.get(f"{self.base_url}/scenes/")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting scenes: {response.text}")
            return []
    
    def start_fresh_conversation(self, scene_id):
        """Start a fresh conversation in a scene"""
        print("🔄 Generating conversation (this may take 1-2 minutes)...")
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/conversation/start", timeout=180)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error starting conversation: {response.text}")
            return None
    
    def save_conversation(self, scene_id):
        """Save the current conversation"""
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/conversation/save")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error saving conversation: {response.text}")
            return None
    
    def discard_conversation(self, scene_id):
        """Discard the current conversation"""
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/conversation/discard")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error discarding conversation: {response.text}")
            return None
    
    def continue_unified_conversation(self, scene_id):
        """Continue the unified conversation with more dialogue"""
        print("🔄 Continuing conversation (this may take 30-60 seconds)...")
        response = self.session.post(f"{self.base_url}/scenes/{scene_id}/conversation/continue", timeout=120)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error continuing conversation: {response.text}")
            return None
    
    def export_story_to_markdown(self, scene_id, filename=None):
        """Export the complete story as a markdown file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cave_story_{timestamp}.md"
        
        print(f"📝 Exporting story to {filename}...")
        
        # Get scene details
        scene_response = self.session.get(f"{self.base_url}/scenes/{scene_id}")
        if scene_response.status_code != 200:
            print("❌ Error getting scene details")
            return None
        
        scene = scene_response.json()
        
        # Get all interactions
        interactions_response = self.session.get(f"{self.base_url}/scenes/{scene_id}/interactions/")
        if interactions_response.status_code != 200:
            print("❌ Error getting interactions")
            return None
        
        interactions = interactions_response.json()
        
        # Get scene summary
        summary_response = self.session.post(f"{self.base_url}/scenes/{scene_id}/summarize")
        summary = None
        if summary_response.status_code == 200:
            summary = summary_response.json()
        
        # Create markdown content
        markdown_content = f"""# {scene['title']}

## Scene Details
- **Environment**: {scene['environment']}
- **Context**: {scene['context']}
- **Weather**: {scene['weather'] or 'Not specified'}
- **Time of Day**: {scene['time_of_day'] or 'Not specified'}
- **Mood**: {scene['mood'] or 'Not specified'}

## Characters
"""
        
        # Add character details
        for char in scene.get('characters', []):
            markdown_content += f"""
### {char['name']}
- **Personality**: {char['personality']}
- **Background**: {char['background']}
- **Goals**: {char.get('goals', 'Not specified')}
- **Fears**: {char.get('fears', 'Not specified')}
"""
        
        # Add summary if available
        if summary and not summary.get('error'):
            markdown_content += f"""
## Scene Summary
{summary.get('summary', 'No summary available')}

### Key Events
"""
            for event in summary.get('key_events', []):
                markdown_content += f"- {event}\n"
            
            markdown_content += "\n### Character Developments\n"
            for char, development in summary.get('character_developments', {}).items():
                markdown_content += f"- **{char}**: {development}\n"
            
            markdown_content += f"\n### Plot Advancement\n{summary.get('plot_advancement', 'No plot advancement noted')}\n"
        
        # Add all interactions
        markdown_content += f"""
## Complete Dialogue

*Total interactions: {len(interactions)}*

"""
        
        for i, interaction in enumerate(interactions, 1):
            markdown_content += f"""
### Interaction {i}
**{interaction['character_name']}** ({interaction['emotional_state']}): {interaction['content']}

"""
        
        # Add metadata
        markdown_content += f"""
---
*Generated by Cave - AI-Powered Interactive Storytelling*
*Exported on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*Total interactions: {len(interactions)}*
"""
        
        # Write to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            print(f"✅ Story exported successfully to {filename}")
            return filename
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            return None

def interactive_session():
    """Interactive session for creating scenes and generating conversations"""
    cave = CaveInteractive()
    
    print("🎭 Cave - Interactive Story Creation")
    print("=" * 50)
    print()
    
    # Check if server is running
    if not cave.check_server():
        print("❌ Server is not running. Please start the backend first:")
        print("   make run-backend")
        return
    
    print("✅ Server is running!")
    print()
    
    while True:
        print(f"\n🤖 Current AI Model: {cave.get_model()}")
        print("\n📋 Available Actions:")
        print("1. Create new characters")
        print("2. Create new scene")
        print("3. View existing characters")
        print("4. View existing scenes")
        print("5. Start fresh conversation in a scene")
        print("6. Continue unified conversation (add more dialogue)")
        print("7. Individual character interaction")
        print("8. View scene timeline")
        print("9. Summarize scene")
        print("10. Change AI model")
        print("11. Export story to markdown")
        print("12. Exit")
        print()
        
        choice = input("Choose an action (1-12): ").strip()
        
        if choice == "1":
            create_characters_interactive(cave)
        elif choice == "2":
            create_scene_interactive(cave)
        elif choice == "3":
            view_characters(cave)
        elif choice == "4":
            view_scenes(cave)
        elif choice == "5":
            start_conversation(cave)
        elif choice == "6":
            continue_unified_conversation(cave)
        elif choice == "7":
            continue_conversation(cave)
        elif choice == "8":
            view_timeline(cave)
        elif choice == "9":
            summarize_scene_interactive(cave)
        elif choice == "10":
            change_ai_model(cave)
        elif choice == "11":
            export_story_to_markdown(cave)
        elif choice == "12":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

def create_characters_interactive(cave):
    """Interactive character creation"""
    print("\n👥 Creating New Characters")
    print("-" * 30)
    
    while True:
        print("\nEnter character details (or 'done' to finish):")
        name = input("Character name: ").strip()
        if name.lower() == 'done':
            break
        
        personality = input("Personality: ").strip()
        background = input("Background: ").strip()
        appearance = input("Appearance (optional): ").strip() or None
        goals = input("Goals (optional): ").strip() or None
        fears = input("Fears (optional): ").strip() or None
        
        character = cave.create_character(name, personality, background, appearance, goals, fears)
        if character:
            print(f"✅ Created character: {character['name']}")
        else:
            print("❌ Failed to create character")
        
        continue_creating = input("\nCreate another character? (y/n): ").strip().lower()
        if continue_creating != 'y':
            break

def create_scene_interactive(cave):
    """Interactive scene creation"""
    print("\n🎬 Creating New Scene")
    print("-" * 25)
    
    # Get available characters
    characters = cave.get_characters()
    if not characters:
        print("❌ No characters available. Please create characters first.")
        return
    
    print("\nAvailable characters:")
    for i, char in enumerate(characters, 1):
        print(f"{i}. {char['name']}")
    
    # Get scene details
    title = input("\nScene title: ").strip()
    environment = input("Environment: ").strip()
    context = input("Context: ").strip()
    weather = input("Weather (optional): ").strip() or None
    time_of_day = input("Time of day (optional): ").strip() or None
    mood = input("Mood (optional): ").strip() or None
    
    # Select characters
    print("\nSelect characters for this scene (enter numbers separated by spaces):")
    character_input = input("Character numbers: ").strip()
    try:
        char_indices = [int(x) - 1 for x in character_input.split()]
        character_ids = [characters[i]['id'] for i in char_indices if 0 <= i < len(characters)]
    except:
        print("❌ Invalid character selection")
        return
    
    if len(character_ids) < 2:
        print("❌ Need at least 2 characters for a scene")
        return
    
    scene = cave.create_scene(title, environment, context, character_ids, weather, time_of_day, mood)
    if scene:
        print(f"✅ Created scene: {scene['title']}")
        print(f"   Characters: {len(scene['characters'])}")
        print(f"   Environment: {scene['environment']}")
    else:
        print("❌ Failed to create scene")

def view_characters(cave):
    """View existing characters"""
    print("\n👥 Existing Characters")
    print("-" * 25)
    
    characters = cave.get_characters()
    if not characters:
        print("No characters found.")
        return
    
    for char in characters:
        print(f"\n📝 {char['name']}")
        print(f"   Personality: {char['personality'][:100]}...")
        print(f"   Background: {char['background'][:100]}...")
        if char.get('goals'):
            print(f"   Goals: {char['goals']}")
        if char.get('fears'):
            print(f"   Fears: {char['fears']}")

def view_scenes(cave):
    """View existing scenes"""
    print("\n🎬 Existing Scenes")
    print("-" * 20)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("No scenes found.")
        return
    
    for scene in scenes:
        print(f"\n🎭 {scene['title']}")
        print(f"   Environment: {scene['environment']}")
        print(f"   Context: {scene['context']}")
        print(f"   Characters: {len(scene.get('characters', []))}")
        print(f"   Active: {scene['is_active']}")

def start_conversation(cave):
    """Start a fresh conversation in a scene"""
    print("\n💬 Starting Fresh Conversation")
    print("-" * 30)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available. Please create a scene first.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']} ({len(scene.get('characters', []))} characters)")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            print(f"\n🎬 Starting fresh conversation in: {scene['title']}")
            print(f"   Environment: {scene['environment']}")
            print(f"   Context: {scene['context']}")
            print("\n⚠️  This will clear any existing conversations in this scene.")
            
            confirm = input("Continue? (y/n): ").strip().lower()
            if confirm != 'y':
                print("❌ Cancelled.")
                return
            
            # Start fresh conversation
            print("\n🔄 Generating fresh conversation...")
            result = cave.start_fresh_conversation(scene_id)
            
            if result:
                print(f"\n✅ Generated {result['interactions_generated']} interactions:")
                for interaction in result['interactions']:
                    print(f"\n   👤 {interaction['character_name']} ({interaction['interaction_type']}):")
                    print(f"      {interaction['content']}")
                    print(f"      Emotional state: {interaction['emotional_state']}")
                
                # Ask user if they want to save or discard
                print(f"\n💾 What would you like to do with this conversation?")
                print("1. Save conversation")
                print("2. Discard conversation")
                print("3. View conversation again")
                
                choice = input("\nChoose option (1-3): ").strip()
                
                if choice == "1":
                    save_result = cave.save_conversation(scene_id)
                    if save_result:
                        print(f"✅ Conversation saved! ({save_result['interactions_count']} interactions)")
                    else:
                        print("❌ Failed to save conversation")
                elif choice == "2":
                    discard_result = cave.discard_conversation(scene_id)
                    if discard_result:
                        print(f"🗑️  Conversation discarded! ({discard_result['interactions_deleted']} interactions deleted)")
                    else:
                        print("❌ Failed to discard conversation")
                elif choice == "3":
                    # Show conversation again
                    print(f"\n💬 Generated {result['interactions_generated']} interactions:")
                    for interaction in result['interactions']:
                        print(f"\n   👤 {interaction['character_name']} ({interaction['interaction_type']}):")
                        print(f"      {interaction['content']}")
                        print(f"      Emotional state: {interaction['emotional_state']}")
                    
                    # Ask again
                    choice2 = input("\nSave (s) or discard (d)? ").strip().lower()
                    if choice2 == 's':
                        save_result = cave.save_conversation(scene_id)
                        if save_result:
                            print(f"✅ Conversation saved! ({save_result['interactions_count']} interactions)")
                    elif choice2 == 'd':
                        discard_result = cave.discard_conversation(scene_id)
                        if discard_result:
                            print(f"🗑️  Conversation discarded! ({discard_result['interactions_deleted']} interactions deleted)")
                else:
                    print("❌ Invalid choice. Conversation will be discarded.")
                    cave.discard_conversation(scene_id)
            else:
                print("❌ Failed to start conversation")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

def continue_unified_conversation(cave):
    """Continue unified conversation with more dialogue"""
    print("\n🎭 Continue Unified Conversation")
    print("-" * 35)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']}")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            result = cave.continue_unified_conversation(scene_id)
            if result and result.get('conversation_continued'):
                print(f"\n✅ Conversation continued! Generated {result['interactions_generated']} more interactions.")
                print(f"📊 Total interactions: {result['total_interactions']}")
                print("\n📝 New dialogue:")
                for interaction in result['interactions']:
                    print(f"  {interaction['character_name']}: {interaction['content']}")
                
                # Ask user if they want to continue more
                while True:
                    continue_more = input("\nContinue conversation more? (y/n): ").strip().lower()
                    if continue_more == 'y':
                        result = cave.continue_unified_conversation(scene_id)
                        if result and result.get('conversation_continued'):
                            print(f"\n✅ Added {result['interactions_generated']} more interactions!")
                            print(f"📊 Total interactions: {result['total_interactions']}")
                            print("\n📝 New dialogue:")
                            for interaction in result['interactions']:
                                print(f"  {interaction['character_name']}: {interaction['content']}")
                        else:
                            print("❌ Failed to continue conversation")
                            break
                    elif continue_more == 'n':
                        break
                    else:
                        print("Please enter 'y' or 'n'")
            else:
                print("❌ Failed to continue conversation")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

def continue_conversation(cave):
    """Continue conversation with individual character interactions"""
    print("\n🎭 Individual Character Interaction")
    print("-" * 35)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']}")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            # Get characters in the scene
            scene_detail = cave.session.get(f"{cave.base_url}/scenes/{scene_id}").json()
            characters = scene_detail.get('characters', [])
            
            if not characters:
                print("❌ No characters in this scene")
                return
            
            print(f"\nCharacters in {scene['title']}:")
            for i, char in enumerate(characters, 1):
                print(f"{i}. {char['name']}")
            
            char_choice = int(input("\nSelect character to speak (number): ")) - 1
            if 0 <= char_choice < len(characters):
                character = characters[char_choice]
                max_length = input("Max interaction length (default 50): ").strip()
                max_length = int(max_length) if max_length.isdigit() else 50
                
                result = cave.generate_individual_interaction(scene_id, character['id'], max_length)
                if result:
                    print(f"\n✅ {result['character_name']} says:")
                    print(f"   {result['content']}")
                    print(f"   Type: {result['interaction_type']}")
                    print(f"   Memory generated: {result['memory_generated']}")
                    print(f"   Feelings updated: {result['feelings_updated']}")
                else:
                    print("❌ Failed to generate interaction")
            else:
                print("❌ Invalid character selection")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

def view_timeline(cave):
    """View scene timeline"""
    print("\n📅 Scene Timeline")
    print("-" * 20)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']}")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            timeline = cave.get_scene_timeline(scene_id)
            if timeline:
                print(f"\n📅 Timeline for: {timeline['scene_title']}")
                print(f"   Total events: {timeline['total_events']}")
                print()
                
                for event in timeline['timeline']:
                    event_type = event['type']
                    if event_type == 'interaction':
                        print(f"📝 {event['character_name']}: {event['content']}")
                    elif event_type == 'memory':
                        print(f"💭 {event['character_name']} remembers: {event['content']}")
                    elif event_type == 'plot_note':
                        print(f"📖 Plot note: {event['content']}")
                    print()
            else:
                print("❌ Failed to get timeline")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

def change_ai_model(cave):
    """Change the AI model being used"""
    print("\n🤖 Change AI Model")
    print("-" * 20)
    print(f"Current model: {cave.get_model()}")
    print()
    print("Available models:")
    print("1. gpt-3.5-turbo (Fast, Cheap, Good quality)")
    print("2. gpt-4 (Slower, Expensive, Best quality)")
    print()
    
    choice = input("Select model (1-2): ").strip()
    
    if choice == "1":
        cave.set_model("gpt-3.5-turbo")
    elif choice == "2":
        cave.set_model("gpt-4")
    else:
        print("❌ Invalid choice. Model unchanged.")

def summarize_scene_interactive(cave):
    """Summarize scene interactively"""
    print("\n📋 Scene Summary")
    print("-" * 20)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']}")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            summary = cave.summarize_scene(scene_id)
            if summary:
                print(f"\n📖 Summary for: {scene['title']}")
                print(f"   Total interactions: {summary['total_interactions']}")
                print()
                
                if 'summary' in summary:
                    print("📋 SCENE SUMMARY:")
                    print(f"   {summary['summary']}")
                    print()
                
                if 'key_events' in summary:
                    print("🎯 KEY EVENTS:")
                    for event in summary['key_events']:
                        print(f"   • {event}")
                    print()
                
                if 'character_developments' in summary:
                    print("👥 CHARACTER DEVELOPMENTS:")
                    for char, development in summary['character_developments'].items():
                        print(f"   • {char}: {development}")
                    print()
                
                if 'plot_advancement' in summary:
                    print("📈 PLOT ADVANCEMENT:")
                    print(f"   {summary['plot_advancement']}")
            else:
                print("❌ Failed to summarize scene")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

def export_story_to_markdown(cave):
    """Export the complete story as a markdown file"""
    print("\n📝 Export Story to Markdown")
    print("-" * 30)
    
    scenes = cave.get_scenes()
    if not scenes:
        print("❌ No scenes available.")
        return
    
    print("\nAvailable scenes:")
    for i, scene in enumerate(scenes, 1):
        print(f"{i}. {scene['title']}")
    
    try:
        scene_choice = int(input("\nSelect scene (number): ")) - 1
        if 0 <= scene_choice < len(scenes):
            scene = scenes[scene_choice]
            scene_id = scene['id']
            
            filename = cave.export_story_to_markdown(scene_id)
            if filename:
                print(f"✅ Story exported successfully to {filename}")
            else:
                print("❌ Failed to export story")
        else:
            print("❌ Invalid scene selection")
    except ValueError:
        print("❌ Invalid input")

if __name__ == "__main__":
    interactive_session() 