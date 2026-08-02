import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { LogOut, Pencil, PenLine, Plus, Trash2, Users } from 'lucide-react'
import { api, ApiError } from '../../../lib/api'
import { useAuth } from '../../auth/lib/AuthContext'
import type { BoardRole, BoardSummary } from '../lib/types'

function formatDate(iso: string): string {
  const date = new Date(iso)
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
}

function RoleBadge({ role }: { role: BoardRole }) {
  const styles: Record<BoardRole, string> = {
    owner: 'bg-blue-50 text-blue-700',
    editor: 'bg-green-50 text-green-700',
    viewer: 'bg-neutral-100 text-neutral-500',
  }
  const label: Record<BoardRole, string> = { owner: 'Owner', editor: 'Editor', viewer: 'Viewer' }
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[role]}`}>
      {label[role]}
    </span>
  )
}

export function BoardsPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [boards, setBoards] = useState<BoardSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editingValue, setEditingValue] = useState('')
  const renameInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let cancelled = false
    api
      .get<BoardSummary[]>('/boards')
      .then((data) => {
        if (!cancelled) setBoards(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Failed to load boards.')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (editingId !== null) {
      renameInputRef.current?.focus()
      renameInputRef.current?.select()
    }
  }, [editingId])

  async function handleCreateBoard() {
    setCreating(true)
    setError(null)
    try {
      const board = await api.post<BoardSummary>('/boards', { name: 'Untitled board' })
      navigate(`/board/${board.id}`)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to create board.')
      setCreating(false)
    }
  }

  async function handleDeleteBoard(boardId: number) {
    if (!window.confirm('Delete this board? This cannot be undone.')) return
    const previous = boards
    setBoards((current) => current.filter((b) => b.id !== boardId))
    try {
      await api.delete(`/boards/${boardId}`)
    } catch (err) {
      setBoards(previous)
      setError(err instanceof ApiError ? err.message : 'Failed to delete board.')
    }
  }

  function startRenaming(board: BoardSummary) {
    setEditingId(board.id)
    setEditingValue(board.name)
  }

  async function commitRename(boardId: number) {
    const name = editingValue.trim()
    setEditingId(null)
    const board = boards.find((b) => b.id === boardId)
    if (!board || !name || name === board.name) return

    const previous = boards
    setBoards((current) => current.map((b) => (b.id === boardId ? { ...b, name } : b)))
    try {
      await api.patch<BoardSummary>(`/boards/${boardId}`, { name })
    } catch (err) {
      setBoards(previous)
      setError(err instanceof ApiError ? err.message : 'Failed to rename board.')
    }
  }

  const owned = boards.filter((b) => b.role === 'owner')
  const shared = boards.filter((b) => b.role !== 'owner')

  function BoardList({ list, allowManage }: { list: BoardSummary[]; allowManage: boolean }) {
    return (
      <ul className="flex flex-col gap-2">
        {list.map((board) => (
          <li
            key={board.id}
            className="group flex items-center justify-between rounded-xl border border-neutral-200 bg-white px-4 py-3 hover:border-blue-300 hover:shadow-sm"
          >
            {editingId === board.id ? (
              <input
                ref={renameInputRef}
                value={editingValue}
                onChange={(e) => setEditingValue(e.target.value)}
                onBlur={() => commitRename(board.id)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') e.currentTarget.blur()
                  if (e.key === 'Escape') setEditingId(null)
                }}
                className="flex-1 rounded border border-blue-300 px-2 py-1 text-sm font-medium text-neutral-800 outline-none"
              />
            ) : (
              <button onClick={() => navigate(`/board/${board.id}`)} className="flex flex-1 items-center gap-2 text-left">
                <div>
                  <p className="font-medium text-neutral-800">{board.name}</p>
                  <p className="text-xs text-neutral-400">Updated {formatDate(board.updated_at)}</p>
                </div>
                <RoleBadge role={board.role} />
              </button>
            )}

            {allowManage && (
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100">
                <button
                  onClick={() => startRenaming(board)}
                  title="Rename board"
                  className="rounded-lg p-2 text-neutral-400 hover:bg-neutral-100 hover:text-neutral-700"
                >
                  <Pencil size={16} />
                </button>
                <button
                  onClick={() => handleDeleteBoard(board.id)}
                  title="Delete board"
                  className="rounded-lg p-2 text-neutral-400 hover:bg-red-50 hover:text-red-600"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            )}
          </li>
        ))}
      </ul>
    )
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      <div className="flex items-center justify-between border-b border-neutral-200 bg-white px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600 text-white">
            <PenLine size={18} />
          </div>
          <span className="text-lg font-semibold text-neutral-800">SyncBoard</span>
        </div>
        <div className="flex items-center gap-3 text-sm text-neutral-600">
          <span>{user?.display_name}</span>
          <button
            onClick={logout}
            title="Log out"
            className="flex items-center gap-1 rounded-lg px-2 py-1.5 hover:bg-neutral-100"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-6 py-10">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-neutral-900">Owned boards</h1>
          <button
            onClick={handleCreateBoard}
            disabled={creating}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            <Plus size={16} />
            New board
          </button>
        </div>

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        {loading ? (
          <p className="text-sm text-neutral-400">Loading…</p>
        ) : owned.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-neutral-300 bg-white py-16 text-center">
            <p className="text-sm text-neutral-500">No boards yet — create your first one.</p>
          </div>
        ) : (
          <BoardList list={owned} allowManage />
        )}

        <div className="mb-4 mt-10 flex items-center gap-2">
          <Users size={18} className="text-neutral-400" />
          <h2 className="text-xl font-semibold text-neutral-900">Shared with me</h2>
        </div>

        {!loading && shared.length === 0 ? (
          <p className="text-sm text-neutral-400">
            Boards someone else invites you to will show up here.
          </p>
        ) : (
          !loading && <BoardList list={shared} allowManage={false} />
        )}
      </div>
    </div>
  )
}
