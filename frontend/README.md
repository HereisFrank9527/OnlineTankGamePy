# Tank Game Frontend

A modern React frontend for the tank battle game built with Vite, TypeScript, and Pixi.js for Canvas rendering.

## Features

- **Authentication**: Login/Register forms with JWT token management
- **Room Lobby**: Browse available rooms, create new rooms, join existing rooms
- **Real-time Game**: Canvas-based gameplay using Pixi.js with WebSocket communication
- **Responsive Design**: Optimized for desktop and mobile devices
- **State Management**: Centralized state management using Zustand
- **Type Safety**: Full TypeScript support with comprehensive type definitions

## Tech Stack

- **React 18** - UI framework with hooks and functional components
- **Vite** - Fast build tool and development server
- **TypeScript** - Type-safe JavaScript
- **Pixi.js** - 2D WebGL renderer for high-performance game graphics
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API communication
- **WebSocket** - Real-time communication for multiplayer gameplay

## Prerequisites

- Node.js (version 18 or higher)
- npm or yarn package manager
- Running backend server (see main project README)

## Installation

1. **Clone and setup the project:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` file with your configuration:**
   ```env
   VITE_API_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

## Development

Start the development server:
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

### Available Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint for code quality
- `npm run type-check` - Run TypeScript type checking

## Architecture

### Project Structure
```
src/
├── components/          # Reusable UI components
├── views/              # Main application views
│   ├── LoginView.tsx   # Authentication forms
│   ├── LobbyView.tsx   # Room lobby interface
│   └── GameView.tsx    # Game canvas and UI
├── store/              # Zustand state management
│   └── index.ts        # Global application state
├── services/           # API and WebSocket services
│   ├── api.ts          # REST API client
│   └── websocket.ts    # WebSocket client
├── game/               # Game engine and logic
│   └── GameEngine.ts   # Pixi.js-based game engine
├── types/              # TypeScript type definitions
│   └── index.ts        # Application types
└── utils/              # Utility functions
```

### State Management

The application uses Zustand for state management with the following stores:

- **AuthStore**: User authentication and JWT token management
- **RoomStore**: Room creation, joining, and lobby management
- **GameStore**: Game state, tank positions, projectiles, scoreboard
- **UIStore**: Navigation between views and error handling

### Game Engine

The `GameEngine` class provides:
- **Canvas Rendering**: Pixi.js-based 2D graphics
- **Tank Rendering**: Visual representation of player tanks
- **Projectile Rendering**: Bullet visualization
- **Map Rendering**: Obstacles, power-ups, and spawn points
- **Input Handling**: Keyboard controls for tank movement and firing
- **State Synchronization**: Real-time updates via WebSocket

### WebSocket Protocol

The frontend communicates with the backend using JSON messages:

#### Outgoing Messages (Client → Server)
```typescript
// Tank state updates
{
  type: 'tank_state_update',
  data: { x, y, rotation, velocity_x, velocity_y }
}

// Projectile firing
{
  type: 'fire',
  data: { x, y, rotation }
}
```

#### Incoming Messages (Server → Client)
```typescript
// Tank state updates from other players
{
  type: 'tank_state_update',
  data: { tank_states: TankState[] }
}

// Projectile updates
{
  type: 'projectile_update',
  data: { projectiles: Projectile[] }
}

// Scoreboard updates
{
  type: 'scoreboard_update',
  data: { players: ScoreboardPlayer[] }
}
```

## Game Controls

- **W / ↑** - Move tank forward
- **S / ↓** - Move tank backward  
- **A / ←** - Rotate tank left
- **D / →** - Rotate tank right
- **Space** - Fire projectile

## API Endpoints

The frontend expects these backend endpoints:

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user

### Rooms
- `GET /rooms` - List available rooms
- `POST /rooms` - Create new room
- `GET /rooms/{code}` - Get room details
- `POST /rooms/{code}/join` - Join room
- `POST /rooms/{code}/leave` - Leave room
- `POST /rooms/{code}/ready/{is_ready}` - Set ready status
- `POST /rooms/{code}/start` - Start game

### WebSocket
- `ws://host/ws/game/{room_code}?token={jwt_token}` - Game communication

## Configuration

### Environment Variables

- `VITE_API_URL` - Backend API base URL (default: http://localhost:8000)
- `VITE_WS_URL` - WebSocket server URL (default: ws://localhost:8000)

### Build Configuration

The project uses Vite configuration in `vite.config.ts`:
- React plugin for JSX transformation
- Port 3000 for development server
- Environment variable definitions

## Deployment

### Production Build
```bash
npm run build
```

This creates optimized files in the `dist/` directory.

### Environment Configuration

For production deployment, set the appropriate environment variables:
```env
VITE_API_URL=https://your-api-domain.com
VITE_WS_URL=wss://your-websocket-domain.com
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend server is running
   - Verify WebSocket URL in environment variables
   - Check browser console for connection errors

2. **API Requests Failing**
   - Verify API URL in environment variables
   - Check if backend authentication is working
   - Ensure JWT tokens are being sent

3. **Game Not Rendering**
   - Check if Pixi.js is loading correctly
   - Verify WebGL support in browser
   - Check browser console for rendering errors

4. **Build Errors**
   - Clear node_modules and reinstall dependencies
   - Check TypeScript version compatibility
   - Verify all environment variables are set

### Browser Compatibility

The application requires modern browser features:
- ES2020 support
- WebGL 1.0
- WebSocket support
- CSS Grid and Flexbox

## Development Guidelines

### Code Style
- Use TypeScript for type safety
- Follow React functional component patterns
- Use Zustand for state management
- Implement proper error handling
- Add loading states for async operations

### Testing
```bash
npm run lint
npm run type-check
```

### Performance Considerations
- Game engine runs at 60 FPS
- WebSocket messages are throttled to prevent spam
- React components use proper dependency arrays
- Pixi.js handles high-performance 2D rendering

## Contributing

1. Follow the established code structure
2. Add TypeScript types for all new features
3. Test WebSocket functionality thoroughly
4. Ensure responsive design for new UI components
5. Update this README for new features

## License

See the main project license for details.
