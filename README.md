# TrendSage 🚀

TrendSage is an AI-powered trend analysis platform that leverages CrewAI and large language models to provide real-time insights and analysis of current trends across various categories.

## Features ✨

- **Real-time Trend Analysis**: Fetch and analyze the latest news and trends using CrewAI
- **AI-Generated Blog Posts**: Automatically generate comprehensive blog posts about trending topics
- **Category-based Organization**: Content organized across multiple categories (Tech, Business, Health, etc.)
- **Interactive Chat**: Chat with AI about any trend analysis using RAG (Retrieval Augmented Generation)
- **Modern UI**: Beautiful, responsive interface with glass-morphism design
- **Dark/Light Mode**: Fully customizable theme with seamless transitions
- **Vector Search**: Efficient content retrieval using pgvector embeddings
- **Supabase Integration**: Robust backend with PostgreSQL and real-time features

## Tech Stack 🛠️

### Backend
- Python with FastAPI
- CrewAI for orchestrating AI agents
- OpenAI GPT-4 for content generation
- Supabase (PostgreSQL) with pgvector
- Vector embeddings for RAG-based chat

### Frontend
- Next.js 14
- Tailwind CSS
- Shadcn/ui components
- Framer Motion animations
- Supabase Auth UI

## Getting Started 🚀

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- Supabase account
- OpenAI API key

### Environment Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/trendsage.git
cd trendsage
```

2. Install frontend dependencies
```bash
cd frontend
npm install
```

3. Install backend dependencies
```bash
cd backend
pip install -r requirements.txt
```

4. Set up environment variables
```bash
# Backend (.env)
OPENAI_API_KEY=your_openai_key
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Frontend (.env.local)
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Running the Application

1. Start the backend server
```bash
cd backend
python run.py
```

2. Start the frontend development server
```bash
cd frontend
npm run dev
```

3. Visit `http://localhost:3000` in your browser

## Project Structure 📁

```
trendsage/
├── backend/
│   ├── api/            # FastAPI routes
│   ├── crew/           # CrewAI agents
│   ├── database/       # Database schemas and utils
│   ├── tools/          # AI tools and utilities
│   └── scripts/        # Utility scripts
├── frontend/
│   ├── app/           # Next.js pages
│   ├── components/    # React components
│   ├── lib/          # Utilities and API client
│   └── public/       # Static assets
```

## Features in Detail 🔍

### Trend Analysis
- Real-time news fetching
- AI-powered trend scoring
- Category classification
- Automated blog generation

### Chat Interface
- RAG-based responses
- Context-aware conversations
- Vector similarity search
- Fallback keyword search

### User Experience
- Responsive design
- Glass-morphism UI
- Animated transitions
- Category-based navigation

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments 🙏

- CrewAI for the AI agent framework
- OpenAI for GPT-4 API
- Supabase for the backend infrastructure
- Vercel for hosting
