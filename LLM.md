# 🤖 LLM Overview: Cave - AI-Powered Interactive Storytelling

## 1. Project Overview

**Cave** is an AI-powered interactive storytelling system designed to create dynamic, character-driven narratives. The core purpose of this repository is to provide a framework where AI-controlled characters interact with each other in a persistent world, developing relationships, memories, and advancing a plot through natural dialogue and actions.

The system is built for writers, developers, and AI enthusiasts who want to experiment with emergent storytelling. It is not a game, but rather an engine for generating narrative content. The primary interaction with the system is through a backend API, with a sample command-line interface provided in `test_interactive.py`.

Key goals of the project:
- **Dynamic Storytelling:** To create stories that evolve organically from character interactions, rather than following a pre-defined script.
- **Character Autonomy:** To simulate characters with distinct personalities, goals, and memories that influence their behavior.
- **Rich Narrative Generation:** To produce high-quality narrative content that includes not just dialogue, but also atmospheric descriptions, character thoughts, and actions.
- **User-Controllable:** To allow a user to set up the initial conditions (characters, scenes) and then guide the story by prompting interactions or letting the AI drive the narrative forward.

## 2. Core Concepts

The application is built around a few core concepts that represent the elements of a story. These are defined as SQLAlchemy models in `backend/models.py` and Pydantic schemas in `backend/schemas.py`.

### Characters
- **Purpose:** Represents the actors in the story.
- **Attributes:** Each character has a `name`, `personality`, `background`, `goals`, and `fears`. These attributes are heavily used in the AI prompts to generate behavior true to the character.
- **Relationships:** The system is designed to track relationships and feelings between characters, although this is an emerging feature.

### Scenes
- **Purpose:** Represents the setting and context for interactions.
- **Attributes:** A scene has a `title`, `environment`, `context`, `weather`, `time_of_day`, and `mood`. These are used to ground the AI-generated interactions in a specific setting.
- **Contains:** A scene contains a set of characters who are present and will participate in the interactions.

### Interactions
- **Purpose:** Represents a single event in the story, such as a piece of dialogue, an action, or a thought.
- **Attributes:** An interaction has `content` (what happened), an `interaction_type` (`dialogue`, `action`, `thought`, `narration`), and an `emotional_state`.
- **Generation:** Interactions are the primary output of the `AIEngine`. They are generated based on a character's personality, the scene's context, and recent events.

### Memories
- **Purpose:** To give characters a sense of history and continuity.
- **Generation:** After an interaction, the `AIEngine` can generate a `Memory` for the participating characters. This memory is a summary of the key takeaways from the interaction.
- **Usage:** Memories are fed back into the prompts for future interactions, influencing how a character behaves based on past events.

### AI Engine (`ai_engine.py`)
- **Purpose:** This is the heart of the application. The `AIEngine` class orchestrates all calls to the OpenAI API.
- **Functionality:** It has methods to generate character interactions, scene narration, memories, and analyze story elements.
- **Prompt Engineering:** The quality of the output is highly dependent on the detailed prompts constructed within this module. These prompts dynamically assemble character profiles, scene context, and recent memories to guide the AI's generation.

## 3. Architecture

The application follows a standard modern Python web service architecture.

### Backend (`backend/`)
- **Framework:** The backend is built using **FastAPI**, a high-performance web framework for Python.
- **Entry Point:** The FastAPI application is defined in `backend/main.py`. This file contains all the API endpoint definitions.
- **Server:** The application is served by **Uvicorn**, as seen in `start_backend.py`.

### Database
- **ORM:** The application uses **SQLAlchemy** as its Object-Relational Mapper (ORM) to interact with the database.
- **Models:** The database schema is defined as Python classes in `backend/models.py`.
- **Database Setup:** The database connection and session management are handled in `backend/database.py`. By default, it uses a local **SQLite** database (`cave.db`), but it can be configured to use other databases via the `DATABASE_URL` environment variable.
- **Initialization:** The `make db-init` command (which calls `backend/database.py`) populates the database with initial sample data, which is very useful for testing.

### Data Validation
- **Pydantic:** FastAPI uses **Pydantic** for data validation and serialization. The Pydantic models (schemas) are defined in `backend/schemas.py`. These ensure that all data flowing into and out of the API is well-structured.

### Project Structure
```
Cave/
├── backend/                 # FastAPI backend source code
│   ├── main.py             # API endpoints
│   ├── ai_engine.py        # Core AI logic and OpenAI API interaction
│   ├── models.py           # SQLAlchemy database models
│   ├── schemas.py          # Pydantic data models (schemas)
│   └── database.py         # Database setup and session management
├── test_interactive.py     # Interactive terminal interface for using the app
├── test_workflow.py        # Scripted test of a full user workflow
├── requirements.txt        # Python dependencies
├── Makefile               # Development commands (run, test, install, etc.)
├── start_backend.py       # Script to run the Uvicorn server
└── LLM.md                 # This file
```

## 4. How to Run and Use

This section provides instructions for setting up and running the application.

### Setup and Installation
1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Set up Environment Variables:**
    - Copy the example environment file: `cp env_example.txt .env`
    - Edit the `.env` file and add your OpenAI API key:
      ```
      OPENAI_API_KEY="your-key-here"
      ```
3.  **Initialize the Database:**
    - This command creates the database tables and populates them with sample data.
    ```bash
    make db-init
    ```

### Running the Backend
- To start the backend server, run:
  ```bash
  make run-backend
  ```
- This will start the FastAPI server on `http://localhost:8000`. The server will automatically reload when code changes are made.

### Using the API
The most direct way to interact with the application is through its REST API. Here are some examples using `curl`.

**1. Create a Character:**
```bash
curl -X POST "http://localhost:8000/characters/" \
-H "Content-Type: application/json" \
-d '{
  "name": "Leo",
  "personality": "A cynical detective who has seen too much.",
  "background": "Haunted by a past case, he is relentless in his pursuit of justice.",
  "goals": "Solve the current mystery.",
  "fears": "Letting another victim down."
}'
```

**2. Create a Scene:**
- First, get the IDs of the characters you want to add to the scene.
- Then, create the scene:
```bash
curl -X POST "http://localhost:8000/scenes/" \
-H "Content-Type: application/json" \
-d '{
  "title": "Midnight Interrogation",
  "environment": "A stark, brightly lit interrogation room.",
  "context": "Leo is interrogating a new suspect.",
  "character_ids": ["character-id-1", "character-id-2"]
}'
```

**3. Generate a Conversation:**
- This endpoint starts a new conversation in a scene, clearing any previous interactions.
```bash
curl -X POST "http://localhost:8000/scenes/{scene_id}/conversation/start"
```

**4. Continue a Conversation:**
- This adds more interactions to an existing conversation.
```bash
curl -X POST "http://localhost:8000/scenes/{scene_id}/conversation/continue"
```

### Using the Interactive CLI
- The `test_interactive.py` script provides a user-friendly command-line interface for testing all the major features of the application.
- To use it, run the backend in one terminal, and in another terminal, run:
  ```bash
  python test_interactive.py
  ```
- This will present a menu of options for creating characters, scenes, generating conversations, and more. This is the recommended way to explore the application's capabilities manually.

## 5. Key Workflows

The repository is designed around a few key workflows. The `test_workflow.py` script provides a good example of a complete workflow.

### Workflow 1: Creating a Story from Scratch

This is the most common workflow for starting a new story.

1.  **Create Characters:**
    - Use the `POST /characters/` endpoint to create 2-4 characters with distinct personalities, backgrounds, and goals.

2.  **Create a Scene:**
    - Use the `POST /scenes/` endpoint to create a scene.
    - Provide a detailed `environment` and `context` for the scene.
    - Pass the character IDs of the characters you want to place in the scene.

3.  **Start the Conversation:**
    - Use the `POST /scenes/{scene_id}/conversation/start` endpoint to generate the first set of interactions.
    - The AI will generate a sequence of interactions between the characters in the scene, establishing their initial dynamics.

4.  **Continue the Conversation:**
    - Use the `POST /scenes/{scene_id}/conversation/continue` endpoint to add more interactions to the scene.
    - This can be done multiple times to develop the plot and character relationships.

5.  **Summarize and Export:**
    - Use the `POST /scenes/{scene_id}/summarize` endpoint to get an AI-generated summary of the scene's events.
    - Use the `export_story.py` script or the functionality in `test_interactive.py` to export the full story to a Markdown file.

### Workflow 2: User-Driven Interaction

This workflow gives the user more control over the story's pacing.

1.  **Setup:** Create characters and a scene as in Workflow 1.

2.  **Individual Interactions:**
    - Instead of generating a full conversation, the user can generate an interaction for a single character at a time.
    - Use the `POST /scenes/{scene_id}/interactions/generate` endpoint, providing the `character_id` of the character who should speak or act next.
    - This allows the user to control the "camera" and focus on specific characters.

3.  **Advance Timeline:**
    - Alternatively, the user can advance the timeline for all characters at once using the `POST /scenes/{scene_id}/timeline/advance` endpoint. This is similar to `conversation/start` but is intended for turn-by-turn advancement.

4.  **View Timeline:**
    - Use the `GET /scenes/{scene_id}/timeline` endpoint to see a chronological log of all events in the scene, including interactions, memories, and plot notes. This is useful for tracking the story's progress.

## 6. AI Engine and Prompting

The core logic of the application resides in the `AIEngine` class in `backend/ai_engine.py`. This module is responsible for all communication with the OpenAI API and for constructing the prompts that generate the narrative content.

### Key Generation Functions

-   **`generate_character_interaction`**: Generates a single interaction for a character. It takes into account the character's personality, the scene context, other characters present, and recent memories.
-   **`generate_unified_scene_conversation`**: This is the most powerful function. It generates a full, multi-turn conversation between all characters in a scene. It is designed to produce natural, plot-driven dialogue.
-   **`generate_memory_from_interaction`**: After an interaction is generated, this function is called to create a `Memory` object for the character, summarizing the key takeaways of the interaction.
-   **`generate_scene_narration`**: Generates atmospheric descriptions of the scene to enrich the narrative.
-   **`summarize_scene_events`**: Analyzes all interactions in a scene and produces a summary of key events, character developments, and plot advancements.

### Prompt Engineering

The quality of the generated content is highly dependent on the prompts sent to the OpenAI API. The `AIEngine` uses a sophisticated prompt engineering strategy.

**Example Prompt for `generate_unified_scene_conversation`:**

The following is a simplified example of the prompt structure used to generate a conversation. The actual prompt is dynamically built with much more detail.

```
Scene: First Meeting at the Diner - Emma has just arrived in town and is trying to get information about the mysterious story she's investigating. She's meeting with Marcus and Sarah to learn about the town's history.
Environment: The cozy local diner, with its worn booths and the smell of coffee and pancakes. It's the heart of the town where everyone gathers.
Characters: Emma Chen, Marcus Thompson, Sarah Martinez

RECENT DIALOGUE:
Emma Chen: So, what can you tell me about the old mansion on the outskirts of town?
Sarah Martinez: Oh, you mean the Sinclair Manor? There are so many legends surrounding that place.

Write 3-5 natural interactions that advance the plot and develop character relationships.

IMPORTANT RULES:
- NO introductions or "Hello, I'm [Name]" - characters already know each other
- Vary who speaks - not everyone needs to speak in every round
- Focus on the mystery/plot: Emma is investigating a mysterious story.
- Make dialogue natural and character-specific
- Include reactions, questions, plans, revelations
- Build on previous dialogue, don't repeat

NARRATIVE WRITING STYLE:
You are writing a novel scene, not just dialogue. Each interaction should include:
- Character actions and movements
- Environmental descriptions
- Atmospheric details

Return JSON:
[
  {"character_name": "Name", "content": "What they say or do", "interaction_type": "dialogue/thought/action/narration", "emotional_state": "feeling", "target_character_id": "who they're talking to"}
]
```

This prompt structure guides the AI to:
-   Understand the context of the scene and characters.
-   Build upon the recent conversation history.
-   Follow specific rules to ensure high-quality, relevant dialogue.
-   Incorporate narrative description, not just dialogue.
-   Return the output in a structured JSON format, which can be easily parsed by the application.

Understanding this prompt structure is key to understanding how "Cave" generates its rich, dynamic stories.
