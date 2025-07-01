from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

from backend.database import get_db, create_tables, init_db
from backend.models import Character, Scene, Interaction, Memory, PlotNote, SceneCharacter, CharacterFeeling
from backend.schemas import (
    CharacterCreate, CharacterUpdate, CharacterResponse,
    SceneCreate, SceneUpdate, SceneResponse,
    InteractionCreate, InteractionResponse,
    MemoryCreate, MemoryResponse,
    PlotNoteCreate, PlotNoteResponse,
    AIInteractionRequest, AIInteractionResponse,
    CharacterAnalysis, SceneAnalysis
)
from backend.ai_engine import AIEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Cave - Character Interaction System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global AI engine instance
ai_engine = AIEngine()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    create_tables()
    init_db()

# Character endpoints
@app.post("/characters/", response_model=CharacterResponse)
def create_character(character: CharacterCreate, db: Session = Depends(get_db)):
    """Create a new character."""
    db_character = Character(**character.dict())
    db.add(db_character)
    db.commit()
    db.refresh(db_character)
    return db_character

@app.get("/characters/", response_model=List[CharacterResponse])
def get_characters(db: Session = Depends(get_db)):
    """Get all characters."""
    return db.query(Character).all()

@app.get("/characters/{character_id}", response_model=CharacterResponse)
def get_character(character_id: str, db: Session = Depends(get_db)):
    """Get a specific character."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return character

@app.put("/characters/{character_id}", response_model=CharacterResponse)
def update_character(character_id: str, character_update: CharacterUpdate, db: Session = Depends(get_db)):
    """Update a character."""
    db_character = db.query(Character).filter(Character.id == character_id).first()
    if not db_character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    update_data = character_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_character, field, value)
    
    db.commit()
    db.refresh(db_character)
    return db_character

@app.delete("/characters/{character_id}")
def delete_character(character_id: str, db: Session = Depends(get_db)):
    """Delete a character."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db.delete(character)
    db.commit()
    return {"message": "Character deleted"}

# Scene endpoints
@app.post("/scenes/", response_model=SceneResponse)
def create_scene(scene: SceneCreate, db: Session = Depends(get_db)):
    """Create a new scene with characters."""
    # Create the scene
    scene_data = scene.dict(exclude={'character_ids'})
    db_scene = Scene(**scene_data)
    db.add(db_scene)
    db.commit()
    db.refresh(db_scene)
    
    # Add characters to the scene
    for character_id in scene.character_ids:
        scene_character = SceneCharacter(
            scene_id=db_scene.id,
            character_id=character_id
        )
        db.add(scene_character)
    
    db.commit()
    db.refresh(db_scene)
    
    # Get characters for response
    characters = db.query(Character).filter(Character.id.in_(scene.character_ids)).all()
    response_data = db_scene.__dict__.copy()
    response_data['characters'] = characters
    
    return response_data

@app.get("/scenes/", response_model=List[SceneResponse])
def get_scenes(db: Session = Depends(get_db)):
    """Get all scenes."""
    scenes = db.query(Scene).all()
    result = []
    for scene in scenes:
        # Get characters in the scene
        scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene.id).all()
        character_ids = [sc.character_id for sc in scene_characters]
        characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
        
        scene_data = scene.__dict__.copy()
        scene_data['characters'] = characters
        result.append(scene_data)
    return result

@app.get("/scenes/{scene_id}", response_model=SceneResponse)
def get_scene(scene_id: str, db: Session = Depends(get_db)):
    """Get a specific scene with its characters."""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get characters in the scene
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    response_data = scene.__dict__.copy()
    response_data['characters'] = characters
    
    return response_data

@app.put("/scenes/{scene_id}/activate")
def activate_scene(scene_id: str, db: Session = Depends(get_db)):
    """Activate a scene for interactions."""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Deactivate all other scenes
    db.query(Scene).update({Scene.is_active: False})
    
    # Activate this scene
    scene.is_active = True
    db.commit()
    
    return {"message": f"Scene '{scene.title}' activated"}

# Interaction endpoints
@app.post("/interactions/", response_model=InteractionResponse)
def create_interaction(interaction: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction."""
    # Get character name for response
    character = db.query(Character).filter(Character.id == interaction.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    db_interaction = Interaction(**interaction.dict())
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    
    # Add character name to response
    response_data = db_interaction.__dict__.copy()
    response_data['character_name'] = character.name
    
    if interaction.target_character_id:
        target_character = db.query(Character).filter(Character.id == interaction.target_character_id).first()
        response_data['target_character_name'] = target_character.name if target_character else None
    
    return response_data

@app.get("/scenes/{scene_id}/interactions/", response_model=List[InteractionResponse])
def get_scene_interactions(scene_id: str, db: Session = Depends(get_db)):
    """Get all interactions for a scene."""
    interactions = db.query(Interaction).filter(Interaction.scene_id == scene_id).order_by(Interaction.created_at).all()
    
    result = []
    for interaction in interactions:
        character = db.query(Character).filter(Character.id == interaction.character_id).first()
        response_data = interaction.__dict__.copy()
        response_data['character_name'] = character.name if character else "Unknown"
        
        if interaction.target_character_id:
            target_character = db.query(Character).filter(Character.id == interaction.target_character_id).first()
            response_data['target_character_name'] = target_character.name if target_character else None
        
        result.append(response_data)
    
    return result

# AI Interaction endpoints
@app.post("/ai/interact/", response_model=AIInteractionResponse)
def generate_ai_interaction(request: AIInteractionRequest, db: Session = Depends(get_db)):
    """Generate an AI-driven character interaction."""
    # Get the character
    character = db.query(Character).filter(Character.id == request.character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get the scene
    scene = db.query(Scene).filter(Scene.id == request.scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get other characters in the scene
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == request.scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters if sc.character_id != request.character_id]
    other_characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Get recent interactions
    recent_interactions = db.query(Interaction).filter(
        Interaction.scene_id == request.scene_id
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Get character memories
    character_memories = db.query(Memory).filter(
        Memory.character_id == request.character_id
    ).order_by(Memory.created_at.desc()).limit(10).all()
    
    # Generate interaction
    ai_result = ai_engine.generate_character_interaction(
        character, scene, other_characters, recent_interactions, character_memories, request.max_length
    )
    
    # Create the interaction in database
    interaction = Interaction(
        scene_id=request.scene_id,
        character_id=request.character_id,
        content=ai_result["content"],
        interaction_type=ai_result["interaction_type"],
        emotional_state=ai_result["emotional_state"],
        target_character_id=ai_result["target_character_id"]
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # Generate memory for this interaction
    memory = ai_engine.generate_memory_from_interaction(character, interaction, scene, other_characters)
    if memory:
        db.add(memory)
        db.commit()
    
    # Prepare response
    response_data = interaction.__dict__.copy()
    response_data['character_name'] = character.name
    
    if interaction.target_character_id:
        target_character = db.query(Character).filter(Character.id == interaction.target_character_id).first()
        response_data['target_character_name'] = target_character.name if target_character else None
    
    return AIInteractionResponse(
        interaction=response_data,
        character_thoughts=ai_result.get("character_thoughts"),
        relationship_insights=ai_result.get("relationship_insights")
    )

@app.post("/ai/narrate/")
def generate_scene_narration(scene_id: str, narration_type: str = "atmospheric", db: Session = Depends(get_db)):
    """Generate narrative description for a scene."""
    # Get the scene
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get characters in the scene
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Get recent interactions
    recent_interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Generate narration
    narration = ai_engine.generate_scene_narration(scene, characters, recent_interactions, narration_type)
    
    return {
        "scene_id": scene_id,
        "narration": narration,
        "narration_type": narration_type,
        "timestamp": datetime.now().isoformat()
    }

# Memory endpoints
@app.post("/memories/", response_model=MemoryResponse)
def create_memory(memory: MemoryCreate, db: Session = Depends(get_db)):
    """Create a new memory."""
    db_memory = Memory(**memory.dict())
    db.add(db_memory)
    db.commit()
    db.refresh(db_memory)
    return db_memory

@app.get("/characters/{character_id}/memories/", response_model=List[MemoryResponse])
def get_character_memories(character_id: str, db: Session = Depends(get_db)):
    """Get all memories for a character."""
    return db.query(Memory).filter(Memory.character_id == character_id).order_by(Memory.created_at.desc()).all()

# Plot Note endpoints
@app.post("/plot-notes/", response_model=PlotNoteResponse)
def create_plot_note(plot_note: PlotNoteCreate, db: Session = Depends(get_db)):
    """Create a new plot note."""
    db_plot_note = PlotNote(**plot_note.dict())
    db.add(db_plot_note)
    db.commit()
    db.refresh(db_plot_note)
    return db_plot_note

@app.get("/scenes/{scene_id}/plot-notes/", response_model=List[PlotNoteResponse])
def get_scene_plot_notes(scene_id: str, db: Session = Depends(get_db)):
    """Get all plot notes for a scene."""
    return db.query(PlotNote).filter(PlotNote.scene_id == scene_id).order_by(PlotNote.created_at.desc()).all()

# Analysis endpoints
@app.get("/characters/{character_id}/analysis/", response_model=CharacterAnalysis)
def analyze_character(character_id: str, db: Session = Depends(get_db)):
    """Analyze a character's development and relationships."""
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get character's interactions and memories
    interactions = db.query(Interaction).filter(Interaction.character_id == character_id).all()
    memories = db.query(Memory).filter(Memory.character_id == character_id).all()
    
    # Get other characters this character has interacted with
    other_character_ids = set()
    for interaction in interactions:
        if interaction.target_character_id:
            other_character_ids.add(interaction.target_character_id)
    
    other_characters = db.query(Character).filter(Character.id.in_(list(other_character_ids))).all()
    
    # Analyze relationships
    relationship_analysis = ai_engine.analyze_character_relationships(
        character, other_characters, interactions, memories
    )
    
    return CharacterAnalysis(
        character_id=character_id,
        current_emotional_state="analyzing...",
        goals_progress={"goal1": 0.5, "goal2": 0.3},
        relationship_changes=relationship_analysis.get("changes", []),
        key_memories=[m.content[:100] + "..." for m in memories[-5:]],
        suggested_actions=relationship_analysis.get("suggestions", [])
    )

@app.get("/scenes/{scene_id}/analysis/", response_model=SceneAnalysis)
def analyze_scene(scene_id: str, db: Session = Depends(get_db)):
    """Analyze a scene's development and generate plot inspiration."""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get scene characters and interactions
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    interactions = db.query(Interaction).filter(Interaction.scene_id == scene_id).all()
    
    # Generate plot inspiration
    plot_inspiration = ai_engine.generate_plot_inspiration(scene, characters, interactions)
    
    return SceneAnalysis(
        scene_id=scene_id,
        overall_mood=scene.mood or "neutral",
        character_dynamics={char.name: {"role": "participant", "engagement": "high"} for char in characters},
        plot_developments=plot_inspiration,
        relationship_insights=["Characters are developing connections", "Tensions are building"],
        writing_inspiration=plot_inspiration
    )

# WebSocket endpoint for real-time updates
@app.websocket("/ws/{scene_id}")
async def websocket_endpoint(websocket: WebSocket, scene_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle real-time interaction updates
            await manager.broadcast(f"Scene {scene_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Scene Timeline and Interaction Management
@app.post("/scenes/{scene_id}/timeline/advance")
def advance_scene_timeline(scene_id: str, db: Session = Depends(get_db)):
    """Advance the scene timeline and generate AI interactions for all characters."""
    # Get the scene and characters
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Get recent interactions for context
    recent_interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Generate interactions for each character
    generated_interactions = []
    for character in characters:
        # Get character memories
        character_memories = db.query(Memory).filter(
            Memory.character_id == character.id
        ).order_by(Memory.created_at.desc()).limit(5).all()
        
        # Generate interaction
        ai_result = ai_engine.generate_character_interaction(
            character, scene, [c for c in characters if c.id != character.id], 
            recent_interactions, character_memories, 50
        )
        
        # Create interaction in database
        interaction = Interaction(
            scene_id=scene_id,
            character_id=character.id,
            content=ai_result["content"],
            interaction_type=ai_result["interaction_type"],
            emotional_state=ai_result["emotional_state"],
            target_character_id=ai_result["target_character_id"]
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        
        # Generate memory for this interaction
        memory = ai_engine.generate_memory_from_interaction(
            character, interaction, scene, [c for c in characters if c.id != character.id]
        )
        if memory:
            db.add(memory)
        
        # Update character feelings
        feelings = ai_engine.update_character_feelings(
            character, interaction, [c for c in characters if c.id != character.id]
        )
        for feeling in feelings:
            db.add(feeling)
        
        generated_interactions.append({
            "character_name": character.name,
            "content": ai_result["content"],
            "interaction_type": ai_result["interaction_type"],
            "emotional_state": ai_result["emotional_state"]
        })
    
    db.commit()
    
    return {
        "scene_id": scene_id,
        "timeline_advanced": True,
        "interactions_generated": len(generated_interactions),
        "interactions": generated_interactions
    }

@app.post("/scenes/{scene_id}/summarize")
def summarize_scene_events(scene_id: str, db: Session = Depends(get_db)):
    """Generate a summary of what happened in the scene and document key events."""
    # Get the scene and all interactions
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at).all()
    
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Generate scene summary with focus on relationships
    summary_prompt = f"""
Analyze this scene and focus on character relationships and developments:

SCENE: {scene.title}
CONTEXT: {scene.context}
ENVIRONMENT: {scene.environment}

CHARACTERS: {[c.name for c in characters]}

INTERACTIONS:
{[f"- {i.character.name}: {i.content}" for i in interactions]}

Analyze and return JSON with:
1. **summary**: 2-3 sentence scene overview
2. **key_events**: 3-5 most important events
3. **character_developments**: how each character changed or revealed themselves
4. **relationship_changes**: specific relationship developments between characters
5. **plot_advancement**: how this moves the story forward

Focus on:
- How characters interact with each other
- What they reveal about themselves
- How relationships evolve
- Emotional dynamics and conflicts
- Story progression

Return ONLY valid JSON:
{{
  "summary": "brief scene overview",
  "key_events": ["event1", "event2", "event3"],
  "character_developments": {{"Character1": "development", "Character2": "development"}},
  "relationship_changes": ["relationship change 1", "relationship change 2"],
  "plot_advancement": "how story progresses"
}}
"""
    
    try:
        response = ai_engine.client.chat.completions.create(
            model="gpt-3.5-turbo",  # Much cheaper
            messages=[
                {"role": "system", "content": "You are a story analyst. Return ONLY valid JSON. Focus on character relationships and developments."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=300,  # Reduced for cost
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON if there's extra text
        try:
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_content = content[start_idx:end_idx]
                summary_data = json.loads(json_content)
            else:
                summary_data = json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in summary: {e}")
            logger.error(f"Raw response: {content}")
            # Fallback summary
            summary_data = {
                "summary": f"Scene '{scene.title}' with {len(interactions)} interactions between {len(characters)} characters.",
                "key_events": [f"{i.character.name}: {i.content[:50]}..." for i in interactions[:3]],
                "character_developments": {c.name: "Participated in scene interactions" for c in characters},
                "relationship_changes": ["Characters interacted in the scene"],
                "plot_advancement": "Scene progressed the story through character interactions"
            }
        
        # Create plot note for the summary
        plot_note = PlotNote(
            scene_id=scene_id,
            content=summary_data["summary"],
            category="scene-summary",
            importance=4
        )
        db.add(plot_note)
        db.commit()
        
        return {
            "scene_id": scene_id,
            "summary": summary_data["summary"],
            "key_events": summary_data["key_events"],
            "character_developments": summary_data["character_developments"],
            "relationship_changes": summary_data["relationship_changes"],
            "plot_advancement": summary_data["plot_advancement"],
            "total_interactions": len(interactions)
        }
        
    except Exception as e:
        logger.error(f"Error generating scene summary: {e}")
        return {
            "scene_id": scene_id,
            "error": "Could not generate summary",
            "total_interactions": len(interactions)
        }

@app.get("/scenes/{scene_id}/timeline")
def get_scene_timeline(scene_id: str, db: Session = Depends(get_db)):
    """Get the complete timeline of events for a scene."""
    # Get scene
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get all interactions ordered by time
    interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at).all()
    
    # Get character feelings
    character_feelings = db.query(CharacterFeeling).filter(
        CharacterFeeling.character_id.in_([i.character_id for i in interactions])
    ).all()
    
    # Get memories
    memories = db.query(Memory).filter(
        Memory.scene_id == scene_id
    ).order_by(Memory.created_at).all()
    
    # Get plot notes
    plot_notes = db.query(PlotNote).filter(
        PlotNote.scene_id == scene_id
    ).order_by(PlotNote.created_at).all()
    
    timeline_events = []
    
    # Add interactions to timeline
    for interaction in interactions:
        character = db.query(Character).filter(Character.id == interaction.character_id).first()
        timeline_events.append({
            "timestamp": interaction.created_at.isoformat(),
            "type": "interaction",
            "character_name": character.name if character else "Unknown",
            "content": interaction.content,
            "interaction_type": interaction.interaction_type,
            "emotional_state": interaction.emotional_state
        })
    
    # Add memories to timeline
    for memory in memories:
        character = db.query(Character).filter(Character.id == memory.character_id).first()
        timeline_events.append({
            "timestamp": memory.created_at.isoformat(),
            "type": "memory",
            "character_name": character.name if character else "Unknown",
            "content": memory.key_points,
            "memory_type": memory.memory_type,
            "importance": memory.importance
        })
    
    # Add plot notes to timeline
    for plot_note in plot_notes:
        timeline_events.append({
            "timestamp": plot_note.created_at.isoformat(),
            "type": "plot_note",
            "content": plot_note.content,
            "category": plot_note.category,
            "importance": plot_note.importance
        })
    
    # Sort by timestamp
    timeline_events.sort(key=lambda x: x["timestamp"])
    
    return {
        "scene_id": scene_id,
        "scene_title": scene.title,
        "total_events": len(timeline_events),
        "timeline": timeline_events,
        "character_feelings": [
            {
                "character_id": cf.character_id,
                "target_character_id": cf.target_character_id,
                "feeling_type": cf.feeling_type,
                "intensity": cf.intensity,
                "reason": cf.reason
            } for cf in character_feelings
        ]
    }

@app.post("/scenes/{scene_id}/interactions/generate")
def generate_character_interaction_for_scene(
    scene_id: str, 
    character_id: str, 
    max_length: int = 50,
    db: Session = Depends(get_db)
):
    """Generate a single AI interaction for a specific character in a scene."""
    # Get the character
    character = db.query(Character).filter(Character.id == character_id).first()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Get the scene
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Get other characters in the scene
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters if sc.character_id != character_id]
    other_characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Get recent interactions
    recent_interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at.desc()).limit(5).all()
    
    # Get character memories
    character_memories = db.query(Memory).filter(
        Memory.character_id == character_id
    ).order_by(Memory.created_at.desc()).limit(5).all()
    
    # Generate interaction
    ai_result = ai_engine.generate_character_interaction(
        character, scene, other_characters, recent_interactions, character_memories, max_length
    )
    
    # Create the interaction in database
    interaction = Interaction(
        scene_id=scene_id,
        character_id=character_id,
        content=ai_result["content"],
        interaction_type=ai_result["interaction_type"],
        emotional_state=ai_result["emotional_state"],
        target_character_id=ai_result["target_character_id"]
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    
    # Generate memory for this interaction
    memory = ai_engine.generate_memory_from_interaction(character, interaction, scene, other_characters)
    if memory:
        db.add(memory)
    
    # Update character feelings
    feelings = ai_engine.update_character_feelings(character, interaction, other_characters)
    for feeling in feelings:
        db.add(feeling)
    
    db.commit()
    
    return {
        "interaction_id": interaction.id,
        "character_name": character.name,
        "content": ai_result["content"],
        "interaction_type": ai_result["interaction_type"],
        "emotional_state": ai_result["emotional_state"],
        "target_character_id": ai_result["target_character_id"],
        "memory_generated": memory is not None,
        "feelings_updated": len(feelings)
    }

@app.post("/scenes/{scene_id}/conversation/start")
def start_fresh_conversation(scene_id: str, db: Session = Depends(get_db)):
    """Start a fresh conversation in a scene, clearing previous interactions."""
    # Get the scene and characters
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Clear all existing interactions for this scene
    db.query(Interaction).filter(Interaction.scene_id == scene_id).delete()
    db.query(Memory).filter(Memory.scene_id == scene_id).delete()
    db.query(CharacterFeeling).filter(CharacterFeeling.character_id.in_(
        [sc.character_id for sc in db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()]
    )).delete()
    db.commit()
    
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Generate unified scene conversation
    try:
        unified_interactions = ai_engine.generate_unified_scene_conversation(scene, characters, 100)
        
        generated_interactions = []
        for interaction_data in unified_interactions:
            # Find character by name
            character = next((c for c in characters if c.name == interaction_data["character_name"]), None)
            if not character:
                continue
            
            # Create interaction in database
            interaction = Interaction(
                scene_id=scene_id,
                character_id=character.id,
                content=interaction_data["content"],
                interaction_type=interaction_data["interaction_type"],
                emotional_state=interaction_data["emotional_state"],
                target_character_id=interaction_data["target_character_id"]
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            generated_interactions.append({
                "character_name": interaction_data["character_name"],
                "content": interaction_data["content"],
                "interaction_type": interaction_data["interaction_type"],
                "emotional_state": interaction_data["emotional_state"]
            })
        
        return {
            "scene_id": scene_id,
            "conversation_started": True,
            "interactions_generated": len(generated_interactions),
            "interactions": generated_interactions
        }
        
    except Exception as e:
        logger.error(f"Error generating unified conversation: {e}")
        return {
            "scene_id": scene_id,
            "conversation_started": False,
            "error": "Failed to generate conversation",
            "interactions_generated": 0,
            "interactions": []
        }

@app.post("/scenes/{scene_id}/conversation/save")
def save_conversation(scene_id: str, db: Session = Depends(get_db)):
    """Save the current conversation (no action needed, just confirmation)."""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    interactions = db.query(Interaction).filter(Interaction.scene_id == scene_id).all()
    
    return {
        "scene_id": scene_id,
        "conversation_saved": True,
        "interactions_count": len(interactions),
        "message": "Conversation has been saved successfully."
    }

@app.post("/scenes/{scene_id}/conversation/discard")
def discard_conversation(scene_id: str, db: Session = Depends(get_db)):
    """Discard the current conversation, clearing all interactions."""
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    # Clear all interactions and related data
    interactions_deleted = db.query(Interaction).filter(Interaction.scene_id == scene_id).delete()
    memories_deleted = db.query(Memory).filter(Memory.scene_id == scene_id).delete()
    
    # Clear character feelings for characters in this scene
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    feelings_deleted = db.query(CharacterFeeling).filter(
        CharacterFeeling.character_id.in_(character_ids)
    ).delete()
    
    db.commit()
    
    return {
        "scene_id": scene_id,
        "conversation_discarded": True,
        "interactions_deleted": interactions_deleted,
        "memories_deleted": memories_deleted,
        "feelings_deleted": feelings_deleted,
        "message": "Conversation has been discarded."
    }

@app.post("/scenes/{scene_id}/conversation/continue")
def continue_conversation(scene_id: str, db: Session = Depends(get_db)):
    """Continue the existing conversation with more dialogue."""
    # Get the scene and characters
    scene = db.query(Scene).filter(Scene.id == scene_id).first()
    if not scene:
        raise HTTPException(status_code=404, detail="Scene not found")
    
    scene_characters = db.query(SceneCharacter).filter(SceneCharacter.scene_id == scene_id).all()
    character_ids = [sc.character_id for sc in scene_characters]
    characters = db.query(Character).filter(Character.id.in_(character_ids)).all()
    
    # Get existing interactions for context
    existing_interactions = db.query(Interaction).filter(
        Interaction.scene_id == scene_id
    ).order_by(Interaction.created_at).all()
    
    if not existing_interactions:
        raise HTTPException(status_code=400, detail="No existing conversation to continue")
    
    # Convert to the format expected by the AI engine
    previous_interactions = []
    for interaction in existing_interactions:
        character = next((c for c in characters if c.id == interaction.character_id), None)
        if character:
            previous_interactions.append({
                "character_name": character.name,
                "content": interaction.content,
                "interaction_type": interaction.interaction_type,
                "emotional_state": interaction.emotional_state,
                "target_character_id": interaction.target_character_id
            })
    
    # Generate continuation
    try:
        new_interactions = ai_engine.generate_unified_scene_conversation(
            scene, characters, 100, previous_interactions
        )
        
        generated_interactions = []
        for interaction_data in new_interactions:
            # Find character by name
            character = next((c for c in characters if c.name == interaction_data["character_name"]), None)
            if not character:
                continue
            
            # Create interaction in database
            interaction = Interaction(
                scene_id=scene_id,
                character_id=character.id,
                content=interaction_data["content"],
                interaction_type=interaction_data["interaction_type"],
                emotional_state=interaction_data["emotional_state"],
                target_character_id=interaction_data["target_character_id"]
            )
            db.add(interaction)
            db.commit()
            db.refresh(interaction)
            
            generated_interactions.append({
                "character_name": interaction_data["character_name"],
                "content": interaction_data["content"],
                "interaction_type": interaction_data["interaction_type"],
                "emotional_state": interaction_data["emotional_state"]
            })
        
        return {
            "scene_id": scene_id,
            "conversation_continued": True,
            "interactions_generated": len(generated_interactions),
            "interactions": generated_interactions,
            "total_interactions": len(existing_interactions) + len(generated_interactions)
        }
        
    except Exception as e:
        logger.error(f"Error continuing conversation: {e}")
        return {
            "scene_id": scene_id,
            "conversation_continued": False,
            "error": "Failed to continue conversation",
            "interactions_generated": 0,
            "interactions": []
        }

@app.post("/ai/model")
def change_ai_model(model: str):
    """Change the AI model being used"""
    ai_engine.set_model(model)
    return {"message": f"AI model changed to {model}", "current_model": ai_engine.model}

@app.get("/ai/model")
def get_ai_model():
    """Get the current AI model"""
    return {"current_model": ai_engine.model}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 