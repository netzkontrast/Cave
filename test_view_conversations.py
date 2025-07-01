#!/usr/bin/env python3
"""View existing conversations"""

import requests
import json

def view_existing_conversations():
    """View existing conversations in scenes"""
    base_url = "http://localhost:8000"
    
    try:
        # Get scenes
        response = requests.get(f"{base_url}/scenes/", timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get scenes")
            return
        
        scenes = response.json()
        if not scenes:
            print("❌ No scenes available")
            return
        
        for scene in scenes:
            scene_id = scene['id']
            print(f"\n🎬 Scene: {scene['title']}")
            print(f"   Environment: {scene['environment']}")
            print(f"   Characters: {len(scene.get('characters', []))}")
            
            # Get interactions for this scene
            response = requests.get(f"{base_url}/scenes/{scene_id}/interactions/", timeout=10)
            if response.status_code == 200:
                interactions = response.json()
                if interactions:
                    print(f"   💬 Interactions ({len(interactions)}):")
                    for i, interaction in enumerate(interactions, 1):
                        print(f"\n      {i}. {interaction['character_name']} ({interaction['interaction_type']}):")
                        print(f"         {interaction['content']}")
                        print(f"         Emotional state: {interaction['emotional_state']}")
                        if interaction.get('target_character_name'):
                            print(f"         Target: {interaction['target_character_name']}")
                else:
                    print("   💬 No interactions yet")
            else:
                print(f"   ❌ Failed to get interactions: {response.status_code}")
                
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    view_existing_conversations() 