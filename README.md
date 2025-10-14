# FitRecs AI - Health & Fitness Content Recommendation System

A complete, production-ready recommendation system for fitness content using hybrid AI approach combining semantic content embeddings and collaborative filtering.

## Architecture Overview

The system uses a hybrid recommendation approach:

1. **Content-based Filtering**
   - Uses sentence-transformers (`all-MiniLM-L6-v2`) to generate embeddings
   - FAISS vector index for efficient similarity search
   - Considers item attributes: title, description, tags, duration, difficulty

2. **Collaborative Filtering**
   - Implicit ALS matrix factorization on user interactions
   - Weighted interaction types (view=1, like=3, complete=5)
   - Handles cold-start with content-based fallback

3. **Hybrid Blending**
   - Combines both signals with configurable weights
   - Score normalization and rank fusion
   - Optional context boost from current item

## Features

- User authentication (JWT)
- Content management (upload CSV/JSON)
- Interaction tracking (view/like/complete)
- Multiple recommendation endpoints
- Admin dashboard for data upload
- Responsive React frontend
- Docker deployment
- Automated tests

## Tech Stack

**Backend**
- FastAPI
- SQLAlchemy + PostgreSQL
- Redis caching
- sentence-transformers
- FAISS
- implicit (ALS)

**Frontend**
- React + Vite
- TypeScript
- Tailwind CSS + Material UI
- Axios

## API Endpoints

### Authentication
- POST `/api/v1/auth/signup` - Create new user
- POST `/api/v1/auth/token` - Get access token
- GET `/api/v1/auth/me` - Get current user

### Content
- GET `/api/v1/items` - List items
- GET `/api/v1/items/search` - Search items
- GET `/api/v1/items/{item_id}` - Get item details
- POST `/api/v1/items/upload` - Upload items CSV
- POST `/api/v1/items/rebuild-index` - Rebuild FAISS index

### Recommendations
- GET `/api/v1/recommend/content/{item_id}` - Similar items
- GET `/api/v1/recommend/collaborative/{user_id}` - User recommendations
- GET `/api/v1/recommend/hybrid/{user_id}` - Hybrid recommendations

### Interactions
- POST `/api/v1/interactions` - Record interaction
- GET `/api/v1/interactions/me` - List my interactions

## Quick Start

1. **Clone the repository**
   \`\`\`bash
   git clone https://github.com/yourusername/fitrecs-ai.git
   cd fitrecs-ai
   \`\`\`

2. **Start services with Docker**
   \`\`\`bash
   docker-compose up --build
   \`\`\`
   This will:
   - Start PostgreSQL and Redis
   - Build and start the backend
   - Run database migrations
   - Seed sample data
   - Start the development server

3. **Run frontend locally**
   \`\`\`bash
   cd frontend
   npm install
   npm run dev
   \`\`\`

4. **Access the services**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API docs: http://localhost:8000/docs

## Development Setup

### Backend

1. Create Python environment:
   \`\`\`bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   \`\`\`

2. Set environment variables:
   \`\`\`bash
   export DATABASE_URL="postgresql://fitrecs:fitrecs123@localhost:5432/fitrecs"
   export REDIS_URL="redis://localhost:6379"
   export SECRET_KEY="your-secret-key"
   \`\`\`

3. Run development server:
   \`\`\`bash
   uvicorn app.main:app --reload
   \`\`\`

### Frontend

1. Install dependencies:
   \`\`\`bash
   cd frontend
   npm install
   \`\`\`

2. Start development server:
   \`\`\`bash
   npm run dev
   \`\`\`

## Testing

### Backend Tests
\`\`\`bash
cd backend
pytest app/tests/
\`\`\`

### Frontend Tests
\`\`\`bash
cd frontend
npm test
\`\`\`

## Sample Data

The repo includes a sample dataset (`data/sample_fitness_items.csv`) with:
- 300+ fitness content items
- Mix of workouts, articles, and videos
- Various difficulty levels and durations
- Rich tags and descriptions

To add your own content:
1. Prepare a CSV with columns: title, type, description, tags, duration, difficulty, media_url
2. Upload via admin dashboard or API endpoint
3. Trigger index rebuild if needed

## Production Deployment

For production:
1. Use proper secrets management
2. Configure proper CORS settings
3. Set up proper SSL/TLS
4. Configure proper Postgres settings
5. Add monitoring and logging
6. Set up proper backup strategy

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.