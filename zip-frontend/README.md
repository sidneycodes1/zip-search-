# Zip Frontend

A modern Next.js application for searching people across podcasts, news, videos, and social media.

## Project Structure

```
zip-frontend/
├── public/                   # Static assets
│   └── fonts/               # Font files (Space Mono, Inter)
├── src/
│   ├── app/                 # Next.js App Router
│   ├── features/            # Feature modules (search, results)
│   ├── components/          # Shared UI components
│   ├── lib/                 # Utilities and services
│   ├── hooks/               # Custom React hooks
│   ├── types/               # TypeScript type definitions
│   └── styles/              # Global styles and tokens
└── Configuration files
```

## Getting Started

### Prerequisites
- Node.js 18+ (recommended)
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`.

### Environment Variables

Create a `.env.local` file in the root directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Build

```bash
npm run build
npm start
```

## Architecture

### Features
- **Search**: Main search form with photo upload
- **Results**: Results dashboard with category filtering

### Key Components
- `SearchForm`: Main entry point with form inputs
- `ResultsDashboard`: Results display with polling
- `CategoryTabs`: Filter results by category

### Services
- `searchService`: Handles search API calls
- `jobService`: Polls job status

## Technology Stack

- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom + shadcn/ui inspired
- **State Management**: React hooks

## Development

All components use the Client Component pattern (`'use client'`) to support interactivity.

Path aliases are configured via `@/*` pointing to `src/*`.

## Contributing

Make changes and test locally before submitting.
