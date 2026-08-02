import { Component, type ReactNode } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
}

interface ErrorBoundaryState {
  error: Error | null
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { error: null }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error }
  }

  componentDidCatch(error: Error) {
    // eslint-disable-next-line no-console
    console.error('[SyncBoard] Board crashed:', error)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="flex h-screen w-screen flex-col items-center justify-center gap-3 bg-neutral-50 px-6 text-center">
          <p className="text-lg font-medium text-neutral-800">Something went wrong on this board</p>
          <p className="max-w-md text-sm text-neutral-500">
            {this.state.error.message || 'An unexpected error occurred.'} Try reloading — if it
            keeps happening, check that <code>VITE_LIVEBLOCKS_PUBLIC_KEY</code> is set correctly in{' '}
            <code>frontend/.env</code>.
          </p>
          <button
            onClick={() => window.location.reload()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Reload
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
