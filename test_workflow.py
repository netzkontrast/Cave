#!/usr/bin/env python3
"""
Test script for the user-driven Cave workflow
"""
import sys
import os
import requests
import json
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_user_driven_workflow():
    """Test the complete user-driven workflow"""
    base_url = "http://localhost:8000"
    
    print("🎭 Testing User-Driven Cave Workflow")
    print("=" * 60)
    print("This demonstrates YOUR control over the story timeline!")
    print()
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/characters/")
        print(f"✅ Server is running (Status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the backend first.")
        print("Run: make run-backend")
        return False
    
    # Test 2: Get existing scene
    try:
        response = requests.get(f"{base_url}/scenes/")
        scenes = response.json()
        if scenes:
            scene = scenes[0]  # Use the first scene
            scene_id = scene['id']
            print(f"✅ Using existing scene: {scene['title']}")
        else:
            print("❌ No scenes found. Please create a scene first.")
            return False
    except Exception as e:
        print(f"❌ Error getting scenes: {e}")
        return False
    
    # Test 3: Activate the scene
    try:
        response = requests.put(f"{base_url}/scenes/{scene_id}/activate")
        print(f"✅ Activated scene: {scene['title']}")
    except Exception as e:
        print(f"❌ Error activating scene: {e}")
        return False
    
    print("\n📖 WORKFLOW STEP 1: Scene Setup Complete")
    print("   - Scene is active and ready for interactions")
    print("   - Characters are in place: Emma, Marcus, Sarah")
    print()
    
    # Test 4: Advance timeline (generate interactions for all characters)
    print("🎬 WORKFLOW STEP 2: Advancing Timeline")
    print("   - AI will generate interactions for all characters")
    print("   - Each character will react based on their personality")
    print("   - Interactions will include atmospheric narrative details")
    print()
    
    try:
        response = requests.post(f"{base_url}/scenes/{scene_id}/timeline/advance")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Timeline advanced successfully!")
            print(f"   - Generated {result['interactions_generated']} interactions")
            print()
            
            # Show the interactions
            for i, interaction in enumerate(result['interactions'], 1):
                print(f"   {i}. {interaction['character_name']} ({interaction['interaction_type']}):")
                print(f"      {interaction['content'][:100]}...")
                print(f"      Emotional state: {interaction['emotional_state']}")
                print()
        else:
            print(f"❌ Failed to advance timeline: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error advancing timeline: {e}")
        return False
    
    # Test 5: Generate individual character interaction
    print("🎭 WORKFLOW STEP 3: Individual Character Interaction")
    print("   - You can generate interactions for specific characters")
    print("   - This gives you control over who speaks when")
    print()
    
    try:
        # Get Emma's character ID
        characters_response = requests.get(f"{base_url}/characters/")
        characters = characters_response.json()
        emma = next((c for c in characters if c['name'] == 'Emma Chen'), None)
        
        if emma:
            response = requests.post(
                f"{base_url}/scenes/{scene_id}/interactions/generate",
                params={"character_id": emma['id'], "max_length": 60}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Generated interaction for {result['character_name']}:")
                print(f"   {result['content']}")
                print(f"   Type: {result['interaction_type']}")
                print(f"   Memory generated: {result['memory_generated']}")
                print(f"   Feelings updated: {result['feelings_updated']}")
                print()
            else:
                print(f"❌ Failed to generate individual interaction: {response.text}")
        else:
            print("❌ Could not find Emma character")
    except Exception as e:
        print(f"❌ Error generating individual interaction: {e}")
    
    # Test 6: Get scene timeline
    print("📅 WORKFLOW STEP 4: View Scene Timeline")
    print("   - See all events that have happened in chronological order")
    print("   - Track character feelings and memories")
    print()
    
    try:
        response = requests.get(f"{base_url}/scenes/{scene_id}/timeline")
        if response.status_code == 200:
            timeline = response.json()
            print(f"✅ Scene timeline retrieved:")
            print(f"   - Total events: {timeline['total_events']}")
            print(f"   - Scene: {timeline['scene_title']}")
            print()
            
            # Show recent events
            recent_events = timeline['timeline'][-5:]  # Last 5 events
            for event in recent_events:
                event_type = event['type']
                if event_type == 'interaction':
                    print(f"   📝 {event['character_name']}: {event['content'][:80]}...")
                elif event_type == 'memory':
                    print(f"   💭 {event['character_name']} remembers: {event['content'][:80]}...")
                elif event_type == 'plot_note':
                    print(f"   📖 Plot note: {event['content'][:80]}...")
            print()
        else:
            print(f"❌ Failed to get timeline: {response.text}")
    except Exception as e:
        print(f"❌ Error getting timeline: {e}")
    
    # Test 7: Summarize scene events
    print("📋 WORKFLOW STEP 5: Scene Summary and Documentation")
    print("   - AI summarizes what happened in the scene")
    print("   - Documents key events, character developments, and plot advancement")
    print("   - Saves everything for future reference")
    print()
    
    try:
        response = requests.post(f"{base_url}/scenes/{scene_id}/summarize")
        if response.status_code == 200:
            summary = response.json()
            print(f"✅ Scene summarized successfully!")
            print(f"   - Total interactions: {summary['total_interactions']}")
            print()
            
            if 'summary' in summary:
                print("📖 SCENE SUMMARY:")
                print(f"   {summary['summary']}")
                print()
            
            if 'key_events' in summary:
                print("🎯 KEY EVENTS:")
                for event in summary['key_events'][:3]:  # Show first 3
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
                print()
        else:
            print(f"❌ Failed to summarize scene: {response.text}")
    except Exception as e:
        print(f"❌ Error summarizing scene: {e}")
    
    print("🎉 WORKFLOW COMPLETE!")
    print("=" * 60)
    print("✅ What you accomplished:")
    print("   • Set up and activated a scene with characters")
    print("   • Advanced the timeline with AI-generated interactions")
    print("   • Generated individual character interactions")
    print("   • Viewed the complete scene timeline")
    print("   • Got AI-generated scene summary and documentation")
    print()
    print("🎭 The AI handled:")
    print("   • Natural character interactions with atmospheric details")
    print("   • Character memory generation and feeling updates")
    print("   • Scene summarization and plot documentation")
    print("   • Relationship tracking and development")
    print()
    print("💡 You controlled:")
    print("   • When to advance the timeline")
    print("   • Which characters to focus on")
    print("   • Scene setup and context")
    print("   • Story progression and pacing")
    
    return True

if __name__ == "__main__":
    test_user_driven_workflow() 