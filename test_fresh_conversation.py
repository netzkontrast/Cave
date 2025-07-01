#!/usr/bin/env python3
"""Test fresh conversation generation"""

import requests
import json
import time

def test_fresh_conversation():
    """Test starting a fresh conversation"""
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
        
        scene = scenes[0]  # Use first scene
        scene_id = scene['id']
        
        print(f"🎬 Starting fresh conversation for: {scene['title']}")
        print(f"   Environment: {scene['environment']}")
        print(f"   Characters: {len(scene.get('characters', []))}")
        
        # Start fresh conversation
        print("\n🔄 Generating fresh conversation...")
        start_time = time.time()
        
        response = requests.post(f"{base_url}/scenes/{scene_id}/conversation/start", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            end_time = time.time()
            
            print(f"✅ Conversation generated in {end_time - start_time:.2f} seconds")
            print(f"   Interactions generated: {result['interactions_generated']}")
            
            # Display the generated interactions
            if result.get('interactions'):
                print("\n💬 Generated Conversations:")
                print("=" * 50)
                for i, interaction in enumerate(result['interactions'], 1):
                    print(f"\n{i}. {interaction['character_name']} ({interaction['interaction_type']}):")
                    print(f"   Emotional state: {interaction['emotional_state']}")
                    print(f"   Content: {interaction['content']}")
                    print("-" * 30)
            else:
                print("❌ No interactions were generated")
                
            # Ask if user wants to save or discard
            print(f"\n💾 What would you like to do?")
            print("1. Save conversation")
            print("2. Discard conversation")
            
            choice = input("\nChoose (1-2): ").strip()
            
            if choice == "1":
                save_response = requests.post(f"{base_url}/scenes/{scene_id}/conversation/save")
                if save_response.status_code == 200:
                    save_result = save_response.json()
                    print(f"✅ Conversation saved! ({save_result['interactions_count']} interactions)")
                else:
                    print("❌ Failed to save conversation")
            elif choice == "2":
                discard_response = requests.post(f"{base_url}/scenes/{scene_id}/conversation/discard")
                if discard_response.status_code == 200:
                    discard_result = discard_response.json()
                    print(f"🗑️  Conversation discarded! ({discard_result['interactions_deleted']} interactions deleted)")
                else:
                    print("❌ Failed to discard conversation")
            else:
                print("❌ Invalid choice. Conversation will be discarded.")
                requests.post(f"{base_url}/scenes/{scene_id}/conversation/discard")
        else:
            print(f"❌ Failed to start conversation: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - the AI generation is taking too long")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend is running")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_fresh_conversation() 