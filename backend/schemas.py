from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum

class InteractionType(str, Enum):
    DIALOGUE = "dialogue"
    THOUGHT = "thought"
    ACTION = "action"
    NARRATION = "narration"

class MemoryType(str, Enum):
    INTERACTION = "interaction"
    OBSERVATION = "observation"
    FEELING = "feeling"
    REVELATION = "revelation"

class PlotNoteCategory(str, Enum):
    CHARACTER_DEVELOPMENT = "character-development"
    RELATIONSHIP = "relationship"
    PLOT_POINT = "plot-point"
    INSPIRATION = "inspiration"
    GENERAL = "general"

# Character schemas
class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    personality: str = Field(..., min_length=10)
    background: str = Field(..., min_length=10)
    appearance: Optional[str] = None
    goals: Optional[str] = None
    fears: Optional[str] = None

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    personality: Optional[str] = Field(None, min_length=10)
    background: Optional[str] = Field(None, min_length=10)
    appearance: Optional[str] = None
    goals: Optional[str] = None
    fears: Optional[str] = None

class CharacterResponse(CharacterBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Character Feeling schemas
class CharacterFeelingBase(BaseModel):
    target_character_id: str
    feeling_type: str = Field(..., min_length=1, max_length=50)  # trust, distrust, affection, anger, respect, etc.
    intensity: float = Field(0.0, ge=-100, le=100)
    reason: Optional[str] = None

class CharacterFeelingCreate(CharacterFeelingBase):
    pass

class CharacterFeelingUpdate(BaseModel):
    feeling_type: Optional[str] = Field(None, min_length=1, max_length=50)
    intensity: Optional[float] = Field(None, ge=-100, le=100)
    reason: Optional[str] = None

class CharacterFeelingResponse(CharacterFeelingBase):
    id: str
    character_id: str
    created_at: datetime
    updated_at: datetime
    target_character_name: str
    
    class Config:
        from_attributes = True

# Relationship Group schemas
class RelationshipGroupBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    relationship_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None

class RelationshipGroupCreate(RelationshipGroupBase):
    character_ids: List[str] = Field(..., min_items=2)

class RelationshipGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    relationship_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None

class RelationshipGroupResponse(RelationshipGroupBase):
    id: str
    created_at: datetime
    updated_at: datetime
    members: List[CharacterResponse]
    
    class Config:
        from_attributes = True

class RelationshipGroupMemberBase(BaseModel):
    character_id: str
    role_in_group: Optional[str] = None

class RelationshipGroupMemberCreate(RelationshipGroupMemberBase):
    pass

class RelationshipGroupMemberResponse(RelationshipGroupMemberBase):
    id: str
    group_id: str
    joined_at: datetime
    character: CharacterResponse
    
    class Config:
        from_attributes = True

# Scene schemas
class SceneBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    environment: str = Field(..., min_length=10)
    context: str = Field(..., min_length=10)
    weather: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: Optional[str] = None

class SceneCreate(SceneBase):
    character_ids: List[str] = Field(..., min_items=2)

class SceneUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    environment: Optional[str] = Field(None, min_length=10)
    context: Optional[str] = Field(None, min_length=10)
    weather: Optional[str] = None
    time_of_day: Optional[str] = None
    mood: Optional[str] = None
    is_active: Optional[bool] = None

class SceneResponse(SceneBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    characters: List[CharacterResponse]
    
    class Config:
        from_attributes = True

# Interaction schemas
class InteractionBase(BaseModel):
    content: str = Field(..., min_length=1)
    interaction_type: InteractionType = InteractionType.DIALOGUE
    emotional_state: Optional[str] = None
    target_character_id: Optional[str] = None
    interaction_date: date = Field(default_factory=date.today)

class InteractionCreate(InteractionBase):
    scene_id: str
    character_id: str

class InteractionResponse(InteractionBase):
    id: str
    scene_id: str
    character_id: str
    created_at: datetime
    character_name: str
    target_character_name: Optional[str] = None
    
    class Config:
        from_attributes = True

# Memory schemas - Updated to use key_points
class MemoryBase(BaseModel):
    key_points: str = Field(..., min_length=1)  # Bullet points of key information
    memory_type: MemoryType = MemoryType.INTERACTION
    emotional_impact: float = Field(0.0, ge=-100, le=100)
    related_characters: Optional[List[str]] = None
    importance: int = Field(1, ge=1, le=5)  # How important this memory is

class MemoryCreate(MemoryBase):
    character_id: str
    scene_id: str

class MemoryResponse(MemoryBase):
    id: str
    character_id: str
    scene_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Plot Note schemas
class PlotNoteBase(BaseModel):
    content: str = Field(..., min_length=1)
    category: PlotNoteCategory = PlotNoteCategory.GENERAL
    importance: int = Field(1, ge=1, le=5)

class PlotNoteCreate(PlotNoteBase):
    scene_id: str
    character_id: Optional[str] = None

class PlotNoteResponse(PlotNoteBase):
    id: str
    scene_id: str
    character_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# AI Interaction schemas
class AIInteractionRequest(BaseModel):
    scene_id: str
    character_id: str
    context: Optional[str] = None
    max_length: Optional[int] = Field(50, ge=10, le=200)

class AIInteractionResponse(BaseModel):
    interaction: InteractionResponse
    character_thoughts: Optional[str] = None
    relationship_insights: Optional[Dict[str, Any]] = None

# Relationship schemas
class RelationshipBase(BaseModel):
    character_id: str
    related_character_id: str
    relationship_type: str
    strength: float = Field(0.0, ge=-100, le=100)

class RelationshipCreate(RelationshipBase):
    pass

class RelationshipResponse(RelationshipBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

# Scene Character schemas
class SceneCharacterBase(BaseModel):
    character_id: str
    role_in_scene: Optional[str] = None
    emotional_state: str = "neutral"
    goals_in_scene: Optional[str] = None

class SceneCharacterCreate(SceneCharacterBase):
    pass

class SceneCharacterResponse(SceneCharacterBase):
    id: str
    scene_id: str
    character: CharacterResponse
    
    class Config:
        from_attributes = True

# Analysis schemas
class CharacterAnalysis(BaseModel):
    character_id: str
    current_emotional_state: str
    goals_progress: Dict[str, float]
    relationship_changes: List[Dict[str, Any]]
    key_memories: List[str]
    suggested_actions: List[str]

class SceneAnalysis(BaseModel):
    scene_id: str
    overall_mood: str
    character_dynamics: Dict[str, Dict[str, Any]]
    plot_developments: List[str]
    relationship_insights: List[str]
    writing_inspiration: List[str]
    
    class Config:
        from_attributes = True

# Scene Narration schemas
class SceneNarrationResponse(BaseModel):
    scene_id: str
    narration: str
    narration_type: str
    timestamp: str
    
    class Config:
        from_attributes = True 