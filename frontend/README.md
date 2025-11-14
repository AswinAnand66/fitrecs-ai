# FitRecs - Frontend

A modern, responsive React frontend for the FitRecs Health & Fitness Content Recommendation System. Built with TypeScript, Material UI, and Tailwind CSS.

## Features

- 🔐 JWT Authentication
- 🎯 Personalized content recommendations
- 💪 Workout and article browsing
- 👤 User profiles with preferences
- 📱 Fully responsive design
- ✨ Modern UI with smooth animations

## Tech Stack

- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite
- **UI Libraries:** 
  - Material UI for components
  - Tailwind CSS for utility classes
  - Framer Motion for animations
- **State Management:** React Context API
- **API Client:** Axios
- **Routing:** React Router v6
- **Notifications:** react-hot-toast

## Project Structure

```
frontend/
├── src/
│   ├── api/                 # API client and types
│   ├── auth/                # Authentication context and components
│   ├── components/          # Reusable UI components
│   ├── pages/              # Route components
│   ├── utils/              # Utility functions and hooks
│   ├── App.tsx             # Root component
│   ├── main.tsx            # Entry point
│   ├── router.tsx          # Route configuration
│   └── theme.ts            # Material UI theme
├── public/                 # Static assets
└── package.json           # Dependencies and scripts
```

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Update `VITE_API_URL` with your backend API URL.

3. Start development server:
   ```bash
   npm run dev
   ```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run typecheck` - Type check with TypeScript

## Component Documentation

### Shared Components

#### `<Navbar />`
Main navigation component with responsive mobile menu.

#### `<ContentCard />`
Card component for displaying workouts, articles, and videos. Supports two variants:
- `default`: Full-size card with description
- `compact`: Smaller card for carousels

#### `<RecommendationCarousel />`
Horizontally scrollable carousel for content recommendations with drag-to-scroll support.

#### `<ProtectedRoute />`
Route wrapper that handles authentication and authorization.

### Pages

#### Home (`/`)
Landing page with trending content and personalized recommendations.

#### Item Detail (`/items/:id`)
Detailed view of a workout, article, or video with related content suggestions.

#### Profile (`/profile`)
User profile showing liked and completed content, plus preference management.

#### Auth Pages (`/login` & `/register`)
Clean, modern authentication forms with validation.

## Docker Support

The frontend can be containerized using the provided Dockerfile:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run with Docker Compose:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://localhost:8000/api
```

## Contributing

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature`
3. Make changes and commit: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request