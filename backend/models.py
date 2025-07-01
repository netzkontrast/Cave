from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Table, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import uuid

Base = declarative_base()

# Association table for character relationships (supports multi-character relationships)
character_relationships = Table(
    'character_relationships',
    Base.metadata,
    Column('character_id', String, ForeignKey('characters.id')),
    Column('related_character_id', String, ForeignKey('characters.id')),
    Column('relationship_type', String),
    Column('strength', Float, default=0.0),
    Column('created_at', DateTime, default=datetime.utcnow)
)

# New table for relationship groups (supports multi-character relationships)
class RelationshipGroup(Base):
    __tablename__ = "relationship_groups"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String)  # e.g., "The Book Club", "The Family", "The Rivals"
    relationship_type = Column(String)  # e.g., "friendship", "family", "rivalry", "romance"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    group_members = relationship("RelationshipGroupMember", back_populates="group")

class RelationshipGroupMember(Base):
    __tablename__ = "relationship_group_members"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("relationship_groups.id"))
    character_id = Column(String, ForeignKey("characters.id"))
    role_in_group = Column(String)  # e.g., "leader", "mediator", "outsider"
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    group = relationship("RelationshipGroup", back_populates="group_members")
    character = relationship("Character")

class Character(Base):
    __tablename__ = "characters"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    personality = Column(Text, nullable=False)
    background = Column(Text, nullable=False)
    appearance = Column(Text)
    goals = Column(Text)
    fears = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - Fixed ambiguity by specifying foreign_keys
    memories = relationship("Memory", back_populates="character")
    interactions = relationship("Interaction", back_populates="character", foreign_keys="Interaction.character_id")
    plot_notes = relationship("PlotNote", back_populates="character")
    group_memberships = relationship("RelationshipGroupMember", back_populates="character")
    feelings_about_others = relationship("CharacterFeeling", back_populates="character", foreign_keys="CharacterFeeling.character_id")

# New model for tracking character feelings about other characters
class CharacterFeeling(Base):
    __tablename__ = "character_feelings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, ForeignKey("characters.id"))  # Character who has the feeling
    target_character_id = Column(String, ForeignKey("characters.id"))  # Character they feel about
    feeling_type = Column(String)  # trust, distrust, affection, anger, respect, etc.
    intensity = Column(Float, default=0.0)  # -100 to 100
    reason = Column(Text)  # Brief reason for the feeling
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    character = relationship("Character", back_populates="feelings_about_others", foreign_keys=[character_id])
    target_character = relationship("Character", foreign_keys=[target_character_id])

class Memory(Base):
    __tablename__ = "memories"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    character_id = Column(String, ForeignKey("characters.id"))
    key_points = Column(Text, nullable=False)  # Bullet points of key information
    memory_type = Column(String, default="interaction")  # interaction, observation, feeling, revelation
    emotional_impact = Column(Float, default=0.0)  # -100 to 100
    related_characters = Column(Text)  # JSON string of character IDs
    scene_id = Column(String, ForeignKey("scenes.id"))
    importance = Column(Integer, default=1)  # 1-5 scale, how important this memory is
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    character = relationship("Character", back_populates="memories")
    scene = relationship("Scene", back_populates="memories")

class Scene(Base):
    __tablename__ = "scenes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    environment = Column(Text, nullable=False)
    context = Column(Text, nullable=False)
    weather = Column(String)
    time_of_day = Column(String)
    mood = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scene_characters = relationship("SceneCharacter", back_populates="scene")
    interactions = relationship("Interaction", back_populates="scene")
    memories = relationship("Memory", back_populates="scene")
    plot_notes = relationship("PlotNote", back_populates="scene")

class SceneCharacter(Base):
    __tablename__ = "scene_characters"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String, ForeignKey("scenes.id"))
    character_id = Column(String, ForeignKey("characters.id"))
    role_in_scene = Column(String)  # protagonist, antagonist, supporting, etc.
    emotional_state = Column(String, default="neutral")
    goals_in_scene = Column(Text)
    
    # Relationships
    scene = relationship("Scene", back_populates="scene_characters")
    character = relationship("Character")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String, ForeignKey("scenes.id"))
    character_id = Column(String, ForeignKey("characters.id"))
    content = Column(Text, nullable=False)
    interaction_type = Column(String, default="dialogue")  # dialogue, thought, action, narration
    emotional_state = Column(String)
    target_character_id = Column(String, ForeignKey("characters.id"))
    interaction_date = Column(Date, default=date.today)  # New field for date sorting
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship("Scene", back_populates="interactions")
    character = relationship("Character", back_populates="interactions", foreign_keys=[character_id])
    target_character = relationship("Character", foreign_keys=[target_character_id])

class PlotNote(Base):
    __tablename__ = "plot_notes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scene_id = Column(String, ForeignKey("scenes.id"))
    character_id = Column(String, ForeignKey("characters.id"))
    content = Column(Text, nullable=False)
    category = Column(String, default="general")  # character-development, relationship, plot-point, inspiration
    importance = Column(Integer, default=1)  # 1-5 scale
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scene = relationship("Scene", back_populates="plot_notes")
    character = relationship("Character", back_populates="plot_notes") 