# Jailbreak System Backend

This is the backend for the Jailbreak System, a platform for testing and evaluating jailbreak attacks against large language models.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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

## Running the Server

Development mode:
```bash
python app.py
```

Production mode:
```bash
gunicorn app:app
```

The server will start on http://localhost:5001

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
- Flask
- SQLAlchemy
- PostgreSQL/SQLite
- JWT for authentication
- OpenAI API integration 