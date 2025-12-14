# Nexar Frontend

A modern React application built with Vite, TypeScript, and Shadcn UI components for the Nexar research project.

## Features

- ⚡️ **Vite** - Lightning-fast build tool and dev server
- ⚛️ **React 18** - Latest React features
- 🎨 **Shadcn UI** - Beautiful and accessible component library
- 🔷 **TypeScript** - Type-safe code
- 🎯 **React Router** - Client-side routing
- 🔄 **TanStack Query** - Powerful data fetching and caching
- 🎭 **Tailwind CSS** - Utility-first CSS framework
- 🎪 **React Hook Form** - Performant form handling
- 📊 **Recharts** - Composable charting library

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** (v18 or higher)
- **Bun** (recommended) or npm/yarn/pnpm

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd nexar/frontend
```

### 2. Install Dependencies

Using Bun (recommended):
```bash
bun install
```

Or using npm:
```bash
npm install
```

### 3. Configure Environment Variables

Create a `.env` file in the frontend directory by copying the example:

```bash
cp .env.example .env
```

Edit the `.env` file and configure the variables according to your setup (see Environment Variables section below).

### 4. Start Development Server

Using Bun:
```bash
bun dev
```

Or using npm:
```bash
npm run dev
```

The application will be available at `http://localhost:8080`

## Environment Variables

Create a `.env` file in the frontend directory with the following variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Base URL for the API backend | `http://localhost:3000/api` |

See `.env.example` for a complete example configuration.

## Available Scripts

- `bun dev` / `npm run dev` - Start development server
- `bun build` / `npm run build` - Build for production
- `bun run build:dev` / `npm run build:dev` - Build for development mode
- `bun run lint` / `npm run lint` - Run ESLint
- `bun preview` / `npm run preview` - Preview production build locally

## Project Structure

```
frontend/
├── public/              # Static assets
├── src/
│   ├── components/      # Reusable React components
│   │   ├── dashboard/   # Dashboard-specific components
│   │   ├── layout/      # Layout components (Header, Sidebar, etc.)
│   │   └── ui/          # Shadcn UI components
│   ├── config/          # Configuration files
│   ├── contexts/        # React contexts (Auth, etc.)
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utility libraries and helpers
│   ├── pages/           # Page components (routes)
│   ├── App.tsx          # Main App component
│   ├── main.tsx         # Application entry point
│   └── index.css        # Global styles
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Example environment configuration
├── components.json      # Shadcn UI configuration
├── package.json         # Dependencies and scripts
├── tailwind.config.ts   # Tailwind CSS configuration
├── tsconfig.json        # TypeScript configuration
└── vite.config.ts       # Vite configuration
```

## Building for Production

To create a production build:

```bash
bun build
# or
npm run build
```

The built files will be in the `dist/` directory.

To preview the production build locally:

```bash
bun preview
# or
npm run preview
```

## Development Guidelines

### Adding New Components

Shadcn UI components can be added using:

```bash
bunx shadcn-ui@latest add [component-name]
# or
npx shadcn-ui@latest add [component-name]
```

### Code Style

- Follow TypeScript best practices
- Use functional components with hooks
- Maintain consistent formatting with ESLint
- Use Tailwind CSS utilities for styling

### Authentication

The application includes authentication context and protected routes. See `src/contexts/AuthContext.tsx` and `AUTH_README.md` for more details.

## Troubleshooting

### Port Already in Use

If port 8080 is already in use, you can change it in `vite.config.ts`:

```typescript
server: {
  host: "::",
  port: 3001, // Change to your preferred port
}
```

### API Connection Issues

Ensure that:
1. The backend API is running
2. `VITE_API_BASE_URL` in `.env` points to the correct backend URL
3. CORS is properly configured on the backend

## Contributing

1. Create a feature branch from `main`
2. Make your changes
3. Run linting: `bun run lint`
4. Test your changes
5. Submit a pull request

## License

See the LICENSE file in the root of the repository.

## Support

For issues and questions, please create an issue in the GitHub repository.
