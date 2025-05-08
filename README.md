# 😈 Jailbreak System

A platform for testing, evaluating, and analyzing jailbreak attacks against large language models. This system provides tools and interfaces for users to assess the robustness of **closed-source** language models against various attack strategies.

## 🐱 Project Overview

The Jailbreak System consists of three main components:

1. **Frontend**: A React-based web interface for interacting with the system
2. **Backend**: A Flask API server handling the core logic and model interactions
3. **Database**: Stores attack patterns, prompts, and results

## 🦾Updates

04/25/2025: Enables real LLM APIs (gpt-4o-mini, gpt-4o-2024-0806, gpt-4-turbo, claude-3.5-sonnet)

05/08/2025: Optimized evaluation logic (Harmful Score >= 4 -> Success)

## 🙌 Demo

### Homepage

![Homepage](demo/Home-Page.png "Homepage")

### Attacks Page

![Attackspage](demo/Attacks-Page.png "AttacksPage")

### Prompts Page

![PromptsPage](demo/Prompts-Page.png "PromptsPage")

### Results Page

![ResultsPage](demo/Results-Page.png "ResultsPage")

### Result Details

![Details](demo/Details.png "Details")

### Statistics Page

![StatsPage](demo/Stats-Page.png "StatsPage")

## ⭕ TODOs

This project is still IN PROGRESS:

1. Some baseline attack algos are simple and require polishing.
2. Our own jailbreak method **MIST** is on the way.

## ✳️ Features

- Create and manage jailbreak attacks
- Test attacks against various language models
- Analyze attack success rates and patterns
- Categorize and organize prompts
- Visualize attack results
- Implement custom attack algorithms

## ✅ Supported Attack Algorithms

The system includes several attack algorithms:

1. **Template-based**: Uses predefined templates to construct jailbreak prompts
2. **Character Stuffing**: Adds repeated characters to confuse the model
3. **Multi-language**: Uses foreign language instructions to bypass restrictions
4. **Token Limit**: Adds filler text to push context limits
5. **JSON Injection**: Uses JSON formatting to confuse the model
6. **ASCII Art**: Encodes sensitive words using ASCII art, built upon [ACL24-ArtPrompt](https://github.com/uw-nsl/ArtPrompt)
7. **Cipher**: Uses various cryptographic encoding methods to bypass content moderation, built upon [ICLR24-CipherChat](https://github.com/RobustNLP/CipherChat)

## 🛖 Structure

```
JailbreakSystem/
├── frontend/          # React-based web interface
└── backend/          # Flask API server (includes database)
```

## 🔛 Getting Started

1. Clone the repository:

```bash
git clone https://github.com/SandyyyZheng/JailbreakSystem.git
cd JailbreakSystem
```

2. For documentations, see: 

- [Frontend](frontend/README.md)
- [Backend](backend/README.md)

## 📖 License

This project is MIT-licensed.

## 👻 Acknowledgments

- OpenAI/Anthropic for providing the API
- 2025 Graduation Design for HFUT
- Relies **heavily** on [Cursor](https://www.cursor.com/) (mainly claude-3.5-sonnet & claude-3.7-sonnet) to construct framework and fix bugs. Kudos to AI🤖!