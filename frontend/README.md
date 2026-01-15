# AgentForge — Frontend

React + Vite frontend for AgentForge — a multi-agent AI orchestration UI.

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Framer Motion
- Axios

## Quick start

1. Install dependencies

```bash
cd frontend
npm install
```

2. Run dev server

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

3. Build for production

```bash
npm run build
npm run preview
```

## Important files

- `src/App.jsx` — app entry and page routing (home / about / history / final draft)
- `src/components/` — UI components (Header, InputForm, ResultsPanel, History, FinalDraftView, etc.)
- `src/services/api.js` — Axios API client (exports default `apiService`)
- `vite.config.js` — Vite config (dev proxy)
- `tailwind.config.js` & `postcss.config.cjs` — Tailwind/PostCSS config

## Backend / API

- Dev proxy: Vite forwards `/api/*` to the backend (default `http://localhost:8000`) to avoid CORS in development.
- Optionally set `VITE_API_URL` to a full backend URL to bypass the proxy.

## History & Final Drafts

- The frontend stores minimal history entries locally (only `session_id`, `goal`, `timestamp`).
- Clicking a History item fetches the full report from the backend using `session_id` and opens a dedicated Final Draft page.

## Troubleshooting

- `404 /api/session/:id`: Ensure backend is running and connected to MongoDB and that the `session_id` exists in the `document` collection.
- `PostCSS` errors: ensure `postcss.config.cjs` is present (CommonJS) if your project uses `type: module`.
- `apiService.run is not a function`: confirm `src/services/api.js` exports default `apiService`.
- If Vite shows stale imports after edits, restart the dev server.

## Development notes

- Tailwind theme/colors live in `tailwind.config.js`.
- Animations use Framer Motion — tweak in component props for timing/stagger.
- The UI uses a dark glass theme; keep styling consistent by using the `primary` color utilities in Tailwind.

---

If you'd like, I can also add a `DEVELOPERS.md` with component-level documentation.
# AgentForge Frontend

Modern, animated React UI for the AgentForge multi-agent AI orchestration platform.

## 🚀 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Axios** - HTTP client

## 📦 Installation

```bash
cd frontend
npm install
```

## 🏃 Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🏗️ Build

Create a production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## 🎨 Features

- **Interactive Agent Workflow** - Visual representation of the multi-agent pipeline
- **Real-time Status Updates** - See which agent is currently processing
- **Animated UI** - Smooth transitions and engaging animations
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Dark Theme** - Modern glassmorphism design
- **Session Statistics** - Track API calls and cost savings

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # React components
│   │   ├── Header.jsx
│   │   ├── AgentWorkflow.jsx
│   │   ├── InputForm.jsx
│   │   ├── ResultsPanel.jsx
│   │   └── StatsPanel.jsx
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🔗 API Integration

The frontend is configured to proxy API requests to the backend server running on port 8000. Update the proxy configuration in `vite.config.js` if your backend runs on a different port.

## 🎭 Components

- **Header** - Navigation and branding
- **InputForm** - User input for goal and email
- **AgentWorkflow** - Visual pipeline of agents with real-time status
- **StatsPanel** - Session statistics and metrics
- **ResultsPanel** - Display execution results

## 🌈 Customization

### Colors

Modify the color scheme in `tailwind.config.js`:

```js
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### Animations

Add custom animations in `tailwind.config.js`:

```js
animation: {
  'your-animation': 'keyframe-name duration ease-function',
}
```

## 📝 License

Part of the AgentForge project.
