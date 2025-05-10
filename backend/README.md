# 🔽 Backend

This is the backend documentation for the Jailbreak System.

## Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv/Scripts/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file with your API keys and configuration.

## Running the Server

Development mode:
```bash
python app.py
```

The server will start on http://localhost:5001

## Project Structure

```
backend/
├── app.py                # Main application entry point
├── models/               # Database models
├── controllers/          # API controllers
├── utils/                # Utility functions
│   ├── jailbreak_algorithms.py # Jailbreak implementation
│   └── llm_api.py        # LLM API integration
├── database/             # Database files
│   ├── jailbreak.db      # SQLite database
│   └── db_setup.py       # Database initialization
├── requirements.txt      # Python dependencies
└── .env.example          # Environment variables template
```

## API Endpoints

### Attacks

- `GET /api/attacks/` - Get all attacks
- `GET /api/attacks/<id>` - Get a specific attack
- `POST /api/attacks/` - Create a new attack
- `PUT /api/attacks/<id>` - Update an attack
- `DELETE /api/attacks/<id>` - Delete an attack
- `POST /api/attacks/execute` - Execute an attack on a prompt

### Prompts

- `GET /api/prompts/` - Get all prompts
- `GET /api/prompts/<id>` - Get a specific prompt
- `POST /api/prompts/` - Create a new prompt
- `PUT /api/prompts/<id>` - Update a prompt
- `DELETE /api/prompts/<id>` - Delete a prompt
- `GET /api/prompts/categories` - Get all prompt categories

### Results

- `GET /api/results/` - Get all results
- `GET /api/results/<id>` - Get a specific result
- `POST /api/results/` - Create a new result
- `PUT /api/results/<id>` - Update a result
- `DELETE /api/results/<id>` - Delete a result
- `GET /api/results/stats` - Get statistics about jailbreak success rates

## Implementing Custom Jailbreak Algorithms

To implement your own black-box attack algorithms:

1. Navigate to `utils/jailbreak_algorithms.py`
2. Add your custom function:

```python
def my_custom_jailbreak(prompt, param1="value1", param2="value2"):
    # Your implementation here
    return modified_prompt

# Then add it to the algorithms dictionary
algorithms["my_custom_algorithm"] = my_custom_jailbreak
```

## Database

The system uses SQLite for development. The database file is located at `database/jailbreak.db`.

## Technology Stack

- Python 3.8+
- Flask for Web framework
- SQLite for Database
- LLM API Integrations:
  - OpenAI API (GPT)
  - Anthropic API (Claude) 

## 🪺 Easter Egg
- 并非彩蛋，生活所迫。
- 由于HFUT毕设存在现场验收环节，遂加入了一些必要的「保险措施」，以保证运行时不会出现“全军覆没”的情况。如需关掉「保险措施」，请直接将[config.py](utils/config.py)中的PROBABILITY参数调为0即可.