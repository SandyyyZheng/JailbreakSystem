# Jailbreak System

A comprehensive platform for testing, evaluating, and analyzing jailbreak attacks against large language models. This system provides tools and interfaces for users to assess the robustness of language models against various attack strategies.

## Project Overview

The Jailbreak System consists of three main components:

1. **Frontend**: A React-based web interface for interacting with the system
2. **Backend**: A Flask API server handling the core logic and model interactions
3. **Database**: Stores attack patterns, prompts, and results

## Features

- Create and manage jailbreak attacks
- Test attacks against various language models
- Analyze attack success rates and patterns
- Categorize and organize prompts
- Visualize attack results and statistics
- Implement custom attack algorithms

## Architecture

```
JailbreakSystem/
├── frontend/          # React-based web interface
└── backend/          # Flask API server (includes database)
```

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/SandyyyZheng/JailbreakSystem.git
cd JailbreakSystem
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv/Scripts/activate
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd frontend
npm install
```

4. Configure environment variables:
- Copy `.env.example` to `.env` in both frontend and backend directories
- Update the variables with your configuration

5. Start the services:

Backend:
```bash
cd backend
python app.py
```

Frontend:
```bash
cd frontend
npm run dev
```

## Documentation

- [Frontend Documentation](frontend/README.md)
- [Backend Documentation](backend/README.md)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI/Anthropic for providing the API
- Undergraduate Graduation Design for HFUT
- Relies **heavily** on Claude-3.5-sonnet to construct framework and fix bugs. Kudos to AI!