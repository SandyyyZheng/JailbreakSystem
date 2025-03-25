# 🔼Frontend

This is the frontend documentation for the Jailbreak System.

## Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
```
Then edit the `.env` file with your API configuration.

## Development

Run the development server:

```bash
npm run serve
```

## Build

To build for production:

```bash
npm run build
```

## Features

- Interactive interface for creating and managing jailbreak attacks
- Real-time attack execution and result visualization
- Prompt management system
- Results dashboard with statistics
- Category-based organization of prompts and attacks

## Project Structure

```
frontend/
├── src/
│   ├── views/          # Page components
│   ├── router/         # Vue Router configuration
│   │   └── index.js
│   ├── store/          # Vuex state management
│   │   └── index.js
│   ├── assets/         # Static assets and styles
│   │   └── main.css
│   ├── App.vue         # Root component
│   └── main.js         # Application entry point
├── public/             # Public static assets
├── package.json        # Project dependencies
├── babel.config.js     # Babel configuration
└── .eslintrc.js        # ESLint configuration
```

## Technology Stack

- Vue.js
- Vuex for state management
- Vue Router
- Axios for API communication
- Bootstrap/Vuetify for UI components
