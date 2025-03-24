# bAIby Core Dashboard

Frontend dashboard for bAIby Core service that displays real-time transaction analysis and sentinel status.

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- React 18

## Prerequisites

- Node.js 20+
- npm or yarn
- Docker (if running with Docker)

## Development Setup

1. Install dependencies:
```bash
npm install
# or
yarn install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Update `.env.local` with your settings:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

The app will be available at [http://localhost:3000](http://localhost:3000)

## Docker Setup

1. Build and run with Docker:
```bash
docker build -t baiby-dashboard .
docker run -p 3000:3000 baiby-dashboard
```

2. Or use docker-compose from the root directory:
```bash
docker-compose up --build
```

## Project Structure

```
frontend/
├── src/
│   ├── app/              # Next.js app router
│   ├── components/       # React components
│   ├── types/           # TypeScript types
│   └── lib/             # Utilities and helpers
├── public/              # Static files
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Features

- Real-time transaction monitoring
- Sentinel status tracking
- Request history
- Status statistics

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 