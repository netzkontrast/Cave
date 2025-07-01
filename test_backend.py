#!/usr/bin/env python3
"""
Simple test script for the Cave backend
"""
import sys
import os
import requests
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend():
    """Test the backend API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🚀 Testing Cave Backend API")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/characters/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the backend first.")
        print("Run: cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test 2: Create a character
    character_data = {
        "name": "Alice",
        "personality": "A curious and adventurous young woman who loves exploring new places and meeting people. She's optimistic but sometimes naive.",
        "background": "Alice grew up in a small town and recently moved to the city to pursue her dreams. She works as a freelance writer and is always looking for new stories.",
        "appearance": "Tall with long brown hair, bright green eyes, and a warm smile. She often wears comfortable clothes and carries a notebook.",
        "goals": "To become a successful author and travel the world",
        "fears": "Being alone and missing out on important life experiences"
    }
    
    try:
        response = requests.post(f"{base_url}/characters/", json=character_data)
        if response.status_code == 200:
            alice = response.json()
            print(f"✅ Created character: {alice['name']} (ID: {alice['id']})")
        else:
            print(f"❌ Failed to create character: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating character: {e}")
        return False
    
    # Test 3: Create another character
    character_data2 = {
        "name": "Marcus",
        "personality": "A reserved and analytical detective who prefers to observe before acting. He's experienced but carries the weight of past cases.",
        "background": "Marcus has been a detective for 15 years and has seen the darker side of human nature. He's divorced and lives alone with his cat.",
        "appearance": "Middle-aged with graying hair, sharp blue eyes, and a serious expression. He dresses in practical, dark clothing.",
        "goals": "To solve the current case and find justice for the victims",
        "fears": "Making mistakes that cost innocent lives"
    }
    
    try:
        response = requests.post(f"{base_url}/characters/", json=character_data2)
        if response.status_code == 200:
            marcus = response.json()
            print(f"✅ Created character: {marcus['name']} (ID: {marcus['id']})")
        else:
            print(f"❌ Failed to create character: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating character: {e}")
        return False
    
    # Test 4: Create a scene
    scene_data = {
        "title": "The Coffee Shop Meeting",
        "environment": "A cozy coffee shop in the heart of the city",
        "context": "Alice and Marcus meet for the first time to discuss a mysterious case",
        "weather": "Rainy afternoon",
        "time_of_day": "Afternoon",
        "mood": "Tense and mysterious",
        "character_ids": [alice['id'], marcus['id']]
    }
    
    try:
        response = requests.post(f"{base_url}/scenes/", json=scene_data)
        if response.status_code == 200:
            scene = response.json()
            print(f"✅ Created scene: {scene['title']} (ID: {scene['id']})")
        else:
            print(f"❌ Failed to create scene: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating scene: {e}")
        return False
    
    # Test 5: Activate the scene
    try:
        response = requests.put(f"{base_url}/scenes/{scene['id']}/activate")
        if response.status_code == 200:
            print(f"✅ Activated scene: {scene['title']}")
        else:
            print(f"❌ Failed to activate scene: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error activating scene: {e}")
        return False
    
    # Test 6: Generate AI interaction
    ai_request = {
        "scene_id": scene['id'],
        "character_id": alice['id'],
        "max_length": 50
    }
    
    try:
        response = requests.post(f"{base_url}/ai/interact/", json=ai_request)
        if response.status_code == 200:
            ai_response = response.json()
            print(f"✅ Generated AI interaction:")
            print(f"   Character: {ai_response['interaction']['character_name']}")
            print(f"   Content: {ai_response['interaction']['content'][:100]}...")
            print(f"   Type: {ai_response['interaction']['interaction_type']}")
            print(f"   Emotional State: {ai_response['interaction']['emotional_state']}")
        else:
            print(f"❌ Failed to generate AI interaction: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating AI interaction: {e}")
        return False
    
    # Test 7: Generate scene narration
    try:
        response = requests.post(f"{base_url}/ai/narrate/?scene_id={scene['id']}&narration_type=atmospheric")
        if response.status_code == 200:
            narration = response.json()
            print(f"✅ Generated scene narration:")
            print(f"   Narration: {narration['narration'][:100]}...")
            print(f"   Type: {narration['narration_type']}")
        else:
            print(f"❌ Failed to generate narration: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error generating narration: {e}")
        return False
    
    # Test 8: Get scene interactions
    try:
        response = requests.get(f"{base_url}/scenes/{scene['id']}/interactions/")
        if response.status_code == 200:
            interactions = response.json()
            print(f"✅ Retrieved {len(interactions)} interactions for the scene")
        else:
            print(f"❌ Failed to get interactions: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error getting interactions: {e}")
        return False
    
    print("\n🎉 All tests passed! The backend is working correctly.")
    print("\n📝 Summary:")
    print(f"   - Created 2 characters: {alice['name']} and {marcus['name']}")
    print(f"   - Created 1 scene: {scene['title']}")
    print(f"   - Generated AI interaction with narrative elements")
    print(f"   - Generated atmospheric scene narration")
    print(f"   - Retrieved scene interactions")
    
    return True

if __name__ == "__main__":
    test_backend() 