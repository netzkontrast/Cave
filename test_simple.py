#!/usr/bin/env python3
"""Simple test script for conversation generation"""

import requests
import json
import time

def test_conversation_generation():
    """Test the conversation generation endpoint"""
    base_url = "http://localhost:8000"
    
    # Get scenes
    try:
        response = requests.get(f"{base_url}/scenes/", timeout=10)
        if response.status_code != 200:
            print("❌ Failed to get scenes")
            return
        
        scenes = response.json()
        if not scenes:
            print("❌ No scenes available")
            return
        
        scene = scenes[0]  # Use first scene
        scene_id = scene['id']
        
        print(f"🎬 Testing conversation generation for: {scene['title']}")
        print(f"   Environment: {scene['environment']}")
        print(f"   Characters: {len(scene.get('characters', []))}")
        
        # Test timeline advancement with timeout
        print("\n🔄 Advancing timeline...")
        start_time = time.time()
        
        response = requests.post(f"{base_url}/scenes/{scene_id}/timeline/advance", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            end_time = time.time()
            
            print(f"✅ Timeline advanced successfully in {end_time - start_time:.2f} seconds")
            print(f"   Interactions generated: {result['interactions_generated']}")
            
            # Display the generated interactions
            if result.get('interactions'):
                print("\n💬 Generated Interactions:")
                for i, interaction in enumerate(result['interactions'], 1):
                    print(f"\n   {i}. {interaction['character_name']} ({interaction['interaction_type']}):")
                    print(f"      {interaction['content']}")
                    print(f"      Emotional state: {interaction['emotional_state']}")
            else:
                print("❌ No interactions were generated")
        else:
            print(f"❌ Failed to advance timeline: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - the AI generation is taking too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_conversation_generation() 