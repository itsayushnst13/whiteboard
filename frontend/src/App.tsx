import { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useLocation, useParams } from 'react-router-dom'
import { AuthProvider, useAuth } from './features/auth/lib/AuthContext'
import { LoginPage } from './features/auth/components/LoginPage'
import { RegisterPage } from './features/auth/components/RegisterPage'
import { ProtectedRoute } from './features/auth/components/ProtectedRoute'
import { BoardsPage } from './features/boards/components/BoardsPage'
import type { BoardSummary } from './features/boards/lib/types'
import { BoardPage } from './features/whiteboard/components/BoardPage'
import { api } from './lib/api'

function BoardRoute() {
  const { roomId } = useParams<{ roomId: string }>()
  const location = useLocation()
  const { user } = useAuth()
  const navState = location.state as { name?: string; boardId?: number } | null

  const [board, setBoard] = useState<BoardSummary | null>(
    roomId && navState?.boardId && navState?.name
      ? {
          id: navState.boardId,
          room_id: roomId,
          name: navState.name,
          created_at: '',
          updated_at: '',
        }
      : null,
  )
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!roomId) return
    let cancelled = false
    api
      .get<BoardSummary[]>('/boards')
      .then((boards) => {
        if (cancelled) return
        const match = boards.find((b) => b.room_id === roomId)
        if (match) setBoard(match)
        else setNotFound(true)
      })
      .catch(() => {
        // Keep whatever came from navigation state, if any — the board
        // list is only used to refresh/confirm the name and id.
      })
    return () => {
      cancelled = true
    }
  }, [roomId])

  const handleRename = useCallback(
    async (name: string) => {
      if (!board) return
      await api.patch<BoardSummary>(`/boards/${board.id}`, { name })
      setBoard((prev) => (prev ? { ...prev, name } : prev))
    },
    [board],
  )

  if (!roomId || notFound) return <Navigate to="/boards" replace />

  if (!board) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-neutral-50 text-sm text-neutral-400">
        Loading board…
      </div>
    )
  }

  return (
    <BoardPage
      roomId={roomId}
      boardId={board.id}
      boardName={board.name}
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
            path="/board/:roomId"
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
