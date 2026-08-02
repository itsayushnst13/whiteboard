import { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, Route, Routes, useParams } from 'react-router-dom'
import { AuthProvider, useAuth } from './features/auth/lib/AuthContext'
import { LoginPage } from './features/auth/components/LoginPage'
import { RegisterPage } from './features/auth/components/RegisterPage'
import { ProtectedRoute } from './features/auth/components/ProtectedRoute'
import { BoardsPage } from './features/boards/components/BoardsPage'
import type { BoardSummary } from './features/boards/lib/types'
import { BoardPage } from './features/whiteboard/components/BoardPage'
import { api, ApiError } from './lib/api'

function AccessDenied({ message }: { message: string }) {
  return (
    <div className="flex h-screen w-screen flex-col items-center justify-center gap-3 bg-neutral-50 px-6 text-center">
      <p className="text-lg font-semibold text-neutral-800">{message}</p>
      <p className="text-sm text-neutral-500">
        Ask the board owner to invite you, or check that you copied the right link.
      </p>
      <Link to="/boards" className="mt-2 text-sm font-medium text-blue-600 hover:underline">
        Back to your boards
      </Link>
    </div>
  )
}

function BoardRoute() {
  const { boardId } = useParams<{ boardId: string }>()
  const { user } = useAuth()

  const [board, setBoard] = useState<BoardSummary | null>(null)
  // 'loading' | 'ready' | 'forbidden' | 'not-found' | 'error'
  const [status, setStatus] = useState<'loading' | 'ready' | 'forbidden' | 'not-found' | 'error'>(
    'loading',
  )

  useEffect(() => {
    if (!boardId || Number.isNaN(Number(boardId))) {
      setStatus('not-found')
      return
    }
    let cancelled = false
    setStatus('loading')
    api
      .get<BoardSummary>(`/boards/${boardId}`)
      .then((data) => {
        if (cancelled) return
        setBoard(data)
        setStatus('ready')
      })
      .catch((err) => {
        if (cancelled) return
        if (err instanceof ApiError && err.status === 403) setStatus('forbidden')
        else if (err instanceof ApiError && err.status === 404) setStatus('not-found')
        else setStatus('error')
      })
    return () => {
      cancelled = true
    }
  }, [boardId])

  const handleRename = useCallback(
    async (name: string) => {
      if (!board) return
      await api.patch<BoardSummary>(`/boards/${board.id}`, { name })
      setBoard((prev) => (prev ? { ...prev, name } : prev))
    },
    [board],
  )

  if (status === 'forbidden') {
    return <AccessDenied message="You don't have access to this board." />
  }
  if (status === 'not-found') {
    return <AccessDenied message="This board doesn't exist." />
  }
  if (status === 'error') {
    return <AccessDenied message="Couldn't load this board — check your connection and try again." />
  }
  if (status === 'loading' || !board) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-neutral-50 text-sm text-neutral-400">
        Loading board…
      </div>
    )
  }

  return (
    <BoardPage
      roomId={board.room_id}
      boardId={board.id}
      boardName={board.name}
      role={board.role}
      accountName={user?.display_name}
      onRenameBoard={handleRename}
    />
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/boards"
            element={
              <ProtectedRoute>
                <BoardsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/board/:boardId"
            element={
              <ProtectedRoute>
                <BoardRoute />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/boards" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
