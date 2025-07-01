from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cave.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv("DEBUG", "False").lower() == "true" else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database."""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def init_db():
    """Initialize the database with sample data."""
    from .models import Character, Scene, SceneCharacter
    from .schemas import CharacterCreate, SceneCreate
    
    db = SessionLocal()
    
    try:
        # Check if we already have characters
        existing_characters = db.query(Character).count()
        if existing_characters == 0:
            # Create sample characters
            sample_characters = [
                CharacterCreate(
                    name="Emma Chen",
                    personality="Ambitious journalist with a sharp mind and determination to uncover the truth. She's curious, persistent, and sometimes reckless in her pursuit of stories.",
                    background="Emma moved to this small town to investigate a mysterious story that could make her career. She's from the city and finds the slower pace both charming and frustrating.",
                    appearance="Early 30s, Asian-American, always carries a notebook and camera. Dresses professionally but practically.",
                    goals="Uncover the town's secrets, write a groundbreaking story, prove herself as a journalist",
                    fears="Being wrong about the story, losing her job, being trapped in this small town forever"
                ),
                CharacterCreate(
                    name="Marcus Thompson",
                    personality="Reserved bookstore owner who's lived in the town for decades. He's wise, guarded, and knows more than he lets on. Speaks carefully and thinks deeply.",
                    background="Marcus inherited the bookstore from his father and has been the town's unofficial historian for 20 years. He's seen many people come and go.",
                    appearance="Late 50s, African-American, wears reading glasses, always has a book nearby. Dresses in comfortable, worn clothes.",
                    goals="Protect the town's secrets, help Emma understand the truth, maintain the bookstore's legacy",
                    fears="The past coming back to haunt him, losing the bookstore, being forced to leave town"
                ),
                CharacterCreate(
                    name="Sarah Martinez",
                    personality="Friendly waitress at the local diner who knows everyone in town. She's observant, caring, and has a natural ability to read people. She's the town's social hub.",
                    background="Sarah grew up in the town and has worked at the diner since high school. She knows all the gossip and secrets, but keeps most to herself.",
                    appearance="Mid-20s, Latina, always smiling, wears her hair in a practical ponytail. Dresses in comfortable diner uniform.",
                    goals="Help Emma feel welcome, maintain the town's harmony, find her own path in life",
                    fears="Conflict in the town, losing her job, being stuck in the same place forever"
                )
            ]
            
            characters = []
            for char_data in sample_characters:
                character = Character(
                    name=char_data.name,
                    personality=char_data.personality,
                    background=char_data.background,
                    appearance=char_data.appearance,
                    goals=char_data.goals,
                    fears=char_data.fears
                )
                db.add(character)
                characters.append(character)
            
            db.commit()
            
            # Create a sample scene
            sample_scene = SceneCreate(
                title="First Meeting at the Diner",
                environment="The cozy local diner, with its worn booths and the smell of coffee and pancakes. It's the heart of the town where everyone gathers.",
                context="Emma has just arrived in town and is trying to get information about the mysterious story she's investigating. She's meeting with Marcus and Sarah to learn about the town's history.",
                weather="Sunny morning",
                time_of_day="Breakfast time",
                mood="Curious and slightly tense",
                character_ids=[char.id for char in characters]
            )
            
            scene = Scene(
                title=sample_scene.title,
                environment=sample_scene.environment,
                context=sample_scene.context,
                weather=sample_scene.weather,
                time_of_day=sample_scene.time_of_day,
                mood=sample_scene.mood
            )
            db.add(scene)
            db.commit()
            
            # Add characters to the scene
            for char in characters:
                scene_char = SceneCharacter(
                    scene_id=scene.id,
                    character_id=char.id,
                    role_in_scene="participant",
                    emotional_state="curious",
                    goals_in_scene="Learn about each other and the town"
                )
                db.add(scene_char)
            
            db.commit()
            print("Database initialized with sample data!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close() 