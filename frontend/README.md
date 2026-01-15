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
