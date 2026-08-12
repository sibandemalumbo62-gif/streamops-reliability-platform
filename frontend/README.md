# MediaStream Platform - Frontend

React TypeScript frontend for the MediaStream Platform.

## Prerequisites

- Node.js 18+ 
- npm or yarn

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Development

Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Environment Variables

Create a `.env` file in the frontend directory:
```
VITE_API_URL=http://localhost:8000
```

## Features

- **Dashboard**: Real-time system health monitoring with service status and uptime tracking
- **Media Library**: Browse and search content catalog
- **Authentication**: Login system with JWT token management
- **Responsive Design**: Works on desktop and mobile devices

## API Integration

The frontend connects to the backend API at the URL specified in `VITE_API_URL`. If the backend is not running, the frontend will display mock data for demonstration purposes.

## Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/      # React components
│   ├── Dashboard.tsx
│   ├── Catalog.tsx
│   ├── Login.tsx
│   └── Navigation.tsx
├── services/        # API service layer
│   ├── api.ts
│   ├── auth.ts
│   ├── catalog.ts
│   └── health.ts
├── App.tsx          # Main application component
├── main.tsx         # Application entry point
└── index.css        # Global styles
```

## Technology Stack

- React 18
- TypeScript
- Vite
- React Router
- Axios
- Lucide Icons
