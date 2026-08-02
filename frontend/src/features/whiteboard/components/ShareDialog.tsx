import { useEffect, useState } from 'react'
import { Check, Copy, Loader2, Trash2, X } from 'lucide-react'
import { ApiError } from '../../../lib/api'
import { listCollaborators, removeCollaborator, shareBoard } from '../../boards/lib/collaborators'
import type { BoardRole, Collaborator } from '../../boards/lib/types'

type ShareableRole = Exclude<BoardRole, 'owner'>

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

function initials(name: string) {
  return name
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

interface ShareDialogProps {
  boardId: number
  role: BoardRole
  onClose: () => void
}

export function ShareDialog({ boardId, role, onClose }: ShareDialogProps) {
  const isOwner = role === 'owner'
  const [collaborators, setCollaborators] = useState<Collaborator[] | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [email, setEmail] = useState('')
  const [inviteRole, setInviteRole] = useState<ShareableRole>('editor')
  const [inviting, setInviting] = useState(false)
  const [inviteError, setInviteError] = useState<string | null>(null)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listCollaborators(boardId)
      .then((data) => {
        if (!cancelled) setCollaborators(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setLoadError(err instanceof ApiError ? err.message : 'Failed to load collaborators.')
        }
      })
    return () => {
      cancelled = true
    }
  }, [boardId])

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 2000)
    return () => clearTimeout(t)
  }, [toast])

  function copyLink() {
    const url = `${window.location.origin}/board/${boardId}`
    navigator.clipboard.writeText(url)
    setCopied(true)
    setToast('Share link copied')
    setTimeout(() => setCopied(false), 1500)
  }

  async function handleInvite() {
    const trimmed = email.trim()
    if (!trimmed) return
    setInviting(true)
    setInviteError(null)
    try {
      const collaborator = await shareBoard(boardId, trimmed, inviteRole)
      setCollaborators((prev) => {
        const rest = (prev ?? []).filter((c) => c.user_id !== collaborator.user_id)
        return [...rest, collaborator]
      })
      setEmail('')
      setToast(`Invited ${collaborator.email}`)
    } catch (err) {
      setInviteError(err instanceof ApiError ? err.message : 'Failed to invite that person.')
    } finally {
      setInviting(false)
    }
  }

  async function handleRoleChange(userId: number, newRole: ShareableRole) {
    const previous = collaborators
    setCollaborators((prev) =>
      prev ? prev.map((c) => (c.user_id === userId ? { ...c, role: newRole } : c)) : prev,
    )
    const target = previous?.find((c) => c.user_id === userId)
    if (!target) return
    try {
      await shareBoard(boardId, target.email, newRole)
    } catch (err) {
      setCollaborators(previous ?? null)
      setInviteError(err instanceof ApiError ? err.message : 'Failed to update role.')
    }
  }

  async function handleRemove(userId: number) {
    const previous = collaborators
    setCollaborators((prev) => (prev ? prev.filter((c) => c.user_id !== userId) : prev))
    try {
      await removeCollaborator(boardId, userId)
    } catch (err) {
      setCollaborators(previous ?? null)
      setInviteError(err instanceof ApiError ? err.message : 'Failed to remove collaborator.')
    }
  }

  return (
    <div className="fixed inset-0 z-30 flex items-center justify-center bg-black/30 px-4" onClick={onClose}>
      <div
        className="w-full max-w-md rounded-2xl border border-neutral-200 bg-white p-5 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-neutral-900">Share this board</h2>
          <button onClick={onClose} className="rounded-lg p-1 text-neutral-400 hover:bg-neutral-100">
            <X size={18} />
          </button>
        </div>

        <div className="mb-4 flex items-center gap-2">
          <input
            readOnly
            value={`${window.location.origin}/board/${boardId}`}
            className="flex-1 truncate rounded-lg border border-neutral-200 bg-neutral-50 px-3 py-2 text-sm text-neutral-500"
          />
          <button
            onClick={copyLink}
            className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {copied ? <Check size={14} /> : <Copy size={14} />}
            Copy link
          </button>
        </div>

        {isOwner && (
          <div className="mb-4">
            <label className="mb-1 block text-xs font-medium text-neutral-500">
              Invite by email
            </label>
            <div className="flex items-center gap-2">
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleInvite()}
                placeholder="teammate@example.com"
                className="flex-1 rounded-lg border border-neutral-200 px-3 py-2 text-sm outline-none focus:border-blue-300"
              />
              <select
                value={inviteRole}
                onChange={(e) => setInviteRole(e.target.value as ShareableRole)}
                className="rounded-lg border border-neutral-200 px-2 py-2 text-sm"
              >
                <option value="editor">Editor</option>
                <option value="viewer">Viewer</option>
              </select>
              <button
                onClick={handleInvite}
                disabled={inviting || !email.trim()}
                className="flex items-center gap-1 rounded-lg bg-neutral-900 px-3 py-2 text-sm font-medium text-white hover:bg-neutral-800 disabled:opacity-40"
              >
                {inviting && <Loader2 size={14} className="animate-spin" />}
                Invite
              </button>
            </div>
            {inviteError && <p className="mt-1.5 text-xs text-red-600">{inviteError}</p>}
          </div>
        )}

        <div>
          <p className="mb-2 text-xs font-medium text-neutral-500">Collaborators</p>
          {loadError && <p className="text-xs text-red-600">{loadError}</p>}
          {collaborators === null && !loadError && (
            <p className="text-xs text-neutral-400">Loading…</p>
          )}
          {collaborators !== null && collaborators.length === 0 && (
            <p className="text-xs text-neutral-400">No one else has access yet.</p>
          )}
          <ul className="flex max-h-48 flex-col gap-1 overflow-y-auto">
            {collaborators?.map((c) => (
              <li
                key={c.user_id}
                className="flex items-center justify-between gap-2 rounded-lg px-1 py-1.5 hover:bg-neutral-50"
              >
                <div className="flex min-w-0 items-center gap-2">
                  <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-neutral-300 text-xs font-semibold text-white">
                    {initials(c.display_name || c.email)}
                  </div>
                  <div className="min-w-0">
                    <p className="truncate text-sm text-neutral-800">{c.display_name}</p>
                    <p className="truncate text-xs text-neutral-400">{c.email}</p>
                  </div>
                </div>
                {isOwner ? (
                  <div className="flex shrink-0 items-center gap-1">
                    <select
                      value={c.role}
                      onChange={(e) => handleRoleChange(c.user_id, e.target.value as ShareableRole)}
                      className="rounded-lg border border-neutral-200 px-1.5 py-1 text-xs"
                    >
                      <option value="editor">Editor</option>
                      <option value="viewer">Viewer</option>
                    </select>
                    <button
                      onClick={() => handleRemove(c.user_id)}
                      title="Remove collaborator"
                      className="rounded-lg p-1.5 text-neutral-400 hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ) : (
                  <RoleBadge role={c.role} />
                )}
              </li>
            ))}
          </ul>
        </div>

        {toast && (
          <div className="mt-4 rounded-lg bg-neutral-900 px-3 py-2 text-center text-xs text-white">
            {toast}
          </div>
        )}
      </div>
    </div>
  )
}
