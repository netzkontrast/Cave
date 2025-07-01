# 🎭 Cave - AI-Powered Interactive Storytelling

**Cave** is an AI-driven interactive storytelling system that creates dynamic, character-driven narratives. Watch as AI characters interact, develop relationships, and advance plots in real-time through natural dialogue generation.

## ✨ Features

- **🤖 AI Character Interactions**: Characters speak naturally and respond to each other
- **🎭 Dynamic Storytelling**: Plots evolve through character conversations
- **💬 Natural Dialogue**: No repetitive introductions - real plot-driven conversations
- **💰 Cost Control**: Choose between GPT-3.5-turbo (cheap) and GPT-4 (premium)
- **📊 Scene Management**: Create scenes, add characters, and watch stories unfold
- **🔄 Continue Conversations**: Add more dialogue rounds to develop plots
- **📝 Plot Export**: Export your story as a markdown file
- **🎯 Relationship Tracking**: Characters remember and react to each other

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cave.git
   cd cave
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your OpenAI API key**
   ```bash
   cp env_example.txt .env
   # Edit .env and add your OpenAI API key
   ```

5. **Initialize the database**
   ```bash
   make db-init
   ```

### 🎮 Start Storytelling

1. **Launch the backend**
   ```bash
   make run-backend
   ```

2. **In a new terminal, start the interactive session**
   ```bash
   python test_interactive.py
   ```

3. **Follow the prompts to:**
   - Create characters with personalities
   - Set up scenes with context
   - Generate conversations
   - Continue dialogue
   - Export your story

## 🎭 Interactive Terminal Guide

### Main Menu Options

```
🤖 Current AI Model: gpt-3.5-turbo

📋 Available Actions:
1. Create new characters
2. Create new scene
3. View existing characters
4. View existing scenes
5. Start fresh conversation in a scene
6. Continue unified conversation (add more dialogue)
7. Individual character interaction
8. View scene timeline
9. Summarize scene
10. Change AI model
11. Export story to markdown
12. Exit
```

### 🎯 Recommended Workflow

1. **Create Characters** (Option 1)
   - Give them distinct personalities, backgrounds, goals, and fears
   - Example: A curious journalist, a cautious local, a mysterious stranger

2. **Create a Scene** (Option 2)
   - Set the environment, context, and mood
   - Add 2-4 characters to the scene
   - Example: "Mysterious Meeting at the Diner" with investigation context

3. **Start Fresh Conversation** (Option 5)
   - Watch AI generate natural dialogue between characters
   - No repetitive introductions - real plot development

4. **Continue Conversation** (Option 6)
   - Add more dialogue rounds to develop the story
   - Characters build on previous interactions

5. **Summarize Scene** (Option 9)
   - Get AI analysis of character developments and plot points

6. **Export Story** (Option 11)
   - Save your complete story as a markdown file

### 📝 Exporting Stories

**From Interactive Mode:**
- Use Option 11 to export any scene as a markdown file
- Includes character details, scene summary, and complete dialogue

**From Command Line:**
```bash
python export_story.py
```

**Export includes:**
- Scene details and context
- Character profiles and backgrounds
- AI-generated scene summary
- Key events and character developments
- Complete dialogue with emotional states
- Plot advancement analysis

### 💰 Cost Control

- **GPT-3.5-turbo**: ~$0.01-0.02 per conversation (recommended for testing)
- **GPT-4**: ~$0.10-0.15 per conversation (for important scenes)
- Switch models anytime with Option 10

## 📖 Example Story Session

```
🎭 Cave - Interactive Story Creation
==================================================

✅ Server is running!

🤖 Current AI Model: gpt-3.5-turbo

📋 Available Actions:
1. Create new characters
2. Create new scene
...

Choose an action (1-12): 1

👥 Creating New Characters
--------------------------

Enter character details:
Character name: Emma Chen
Personality: Curious journalist, determined investigator
Background: Recently arrived in town to investigate mysterious disappearances
Goals: Uncover the truth about the missing hiker
Fears: Getting too close to dangerous secrets

✅ Created character: Emma Chen

Choose an action (1-12): 2

🎬 Creating New Scene
---------------------

Scene title: First Meeting at the Diner
Environment: Cozy local diner with worn booths
Context: Emma meets locals to learn about town's mysterious history
Characters: Emma Chen, Sarah Martinez, Marcus Thompson

✅ Created scene: First Meeting at the Diner

Choose an action (1-12): 5

🎬 Starting fresh conversation in: First Meeting at the Diner
⚠️  This will clear any existing conversations in this scene.
Continue? (y/n): y

✅ Generated 4 interactions:

   👤 Emma Chen (dialogue):
      So, what can you tell me about the old mansion on the outskirts of town?
      Emotional state: curious

   👤 Sarah Martinez (dialogue):
      Oh, you mean the Sinclair Manor? There are so many legends surrounding that place.
      Emotional state: intrigued

   👤 Marcus Thompson (dialogue):
      The Sinclair family's history is shrouded in mystery. Tragedy seemed to follow them.
      Emotional state: thoughtful

   👤 Emma Chen (dialogue):
      Do you think there's any truth to the rumors of ghosts haunting the mansion?
      Emotional state: skeptical
```

## 📁 Project Structure

```
Cave/
├── backend/                 # FastAPI backend
│   ├── main.py             # API endpoints
│   ├── ai_engine.py        # AI conversation generation
│   ├── models.py           # Database models
│   └── database.py         # Database setup
├── test_interactive.py     # Interactive terminal interface
├── export_story.py         # Standalone story exporter
├── requirements.txt        # Python dependencies
├── Makefile               # Development commands
└── README.md              # This file
```

## 🛠️ Development

### Available Commands

```bash
make run-backend          # Start the backend server
make db-init              # Initialize the database
make install              # Install dependencies
make test                 # Run tests
```

### API Endpoints

- `POST /characters/` - Create characters
- `POST /scenes/` - Create scenes
- `POST /scenes/{id}/conversation/start` - Start fresh conversation
- `POST /scenes/{id}/conversation/continue` - Continue conversation
- `POST /scenes/{id}/summarize` - Summarize scene
- `GET /ai/model` - Get current AI model
- `POST /ai/model` - Change AI model

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with FastAPI, SQLAlchemy, and OpenAI API
- Inspired by interactive fiction and AI storytelling
- Designed for writers, storytellers, and AI enthusiasts

---

**Ready to create your own AI-driven story? Start with the terminal interface and watch your characters come to life!** 🎭✨ 