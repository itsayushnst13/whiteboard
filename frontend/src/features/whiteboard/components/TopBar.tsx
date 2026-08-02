import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowLeft, Check, Download, Link as LinkIcon, PenLine } from 'lucide-react'
import { useMyPresence, useOthers, useSelf, useStatus } from '../lib/liveblocks'
import { setStoredName } from '../lib/identity'
import type { BoardHandle } from './Board'

function initials(name: string) {
  return name
    .split(' ')
    .map((p) => p[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
}

interface TopBarProps {
  boardId: number
  boardName: string
  onRenameBoard: (name: string) => Promise<void>
  exportRef: React.MutableRefObject<BoardHandle | null>
}

export function TopBar({ boardId, boardName, onRenameBoard, exportRef }: TopBarProps) {
  const others = useOthers()
  const self = useSelf()
  const [presence, updatePresence] = useMyPresence()
  const status = useStatus()
  const [copied, setCopied] = useState(false)
  const [editingName, setEditingName] = useState(false)
  const [displayName, setDisplayName] = useState(boardName)
  const [renameError, setRenameError] = useState<string | null>(null)

  useEffect(() => {
    setDisplayName(boardName)
  }, [boardName])

  async function commitBoardName(value: string) {
    setEditingName(false)
    const name = value.trim()
    if (!name || name === displayName) return

    const previous = displayName
    setDisplayName(name)
    try {
      await onRenameBoard(name)
    } catch (err) {
      // eslint-disable-next-line no-console
      console.error('[SyncBoard] Failed to rename board:', err)
      setDisplayName(previous)
      setRenameError("Couldn't rename the board.")
      setTimeout(() => setRenameError(null), 2500)
    }
  }

  const visibleOthers = others.slice(0, 3)
  const overflow = others.length - visibleOthers.length

  return (
    <div className="absolute inset-x-0 top-0 z-20">
    <div className="flex items-center justify-between border-b border-neutral-200 bg-white/90 px-4 py-2 backdrop-blur">
      <div className="flex items-center gap-2">
        <Link
          to="/boards"
          title="Back to your boards"
          className="flex h-7 w-7 items-center justify-center rounded-lg text-neutral-500 hover:bg-neutral-100"
        >
          <ArrowLeft size={16} />
        </Link>
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600 text-white">
          <PenLine size={16} />
        </div>
        {editingName ? (
          <input
            key={boardId}
            autoFocus
            defaultValue={displayName}
            onBlur={(e) => commitBoardName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') e.currentTarget.blur()
              if (e.key === 'Escape') setEditingName(false)
            }}
            className="w-48 rounded border border-blue-300 px-2 py-0.5 text-sm font-medium outline-none"
          />
        ) : (
          <button
            onClick={() => setEditingName(true)}
            title="Rename this board"
            className="font-medium text-neutral-800 hover:underline"
          >
            {displayName}
          </button>
        )}
        {renameError && <span className="text-xs text-red-600">{renameError}</span>}
        <span
          className={`ml-2 h-2 w-2 rounded-full ${status === 'connected' ? 'bg-green-500' : 'bg-amber-500'}`}
          title={status}
        />
      </div>

      <div className="flex items-center gap-3">
        <PresenceNameEditor presence={presence} updatePresence={updatePresence} />

        <div className="flex -space-x-2">
          {self && (
            <div
              className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white text-xs font-semibold text-white"
              style={{ backgroundColor: presence.color }}
              title={`${presence.name} (you)`}
            >
              {initials(presence.name)}
            </div>
          )}
          {visibleOthers.map((other) => (
            <div
              key={other.connectionId}
              className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white text-xs font-semibold text-white"
              style={{ backgroundColor: other.presence.color }}
              title={other.presence.name}
            >
              {initials(other.presence.name || 'Guest')}
            </div>
          ))}
          {overflow > 0 && (
            <div className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-neutral-400 text-xs font-semibold text-white">
              +{overflow}
            </div>
          )}
        </div>

        <button
          onClick={() => {
            navigator.clipboard.writeText(window.location.href)
            setCopied(true)
            setTimeout(() => setCopied(false), 1500)
          }}
          className="flex items-center gap-1.5 rounded-lg border border-neutral-300 px-3 py-1.5 text-sm text-neutral-700 hover:bg-neutral-50"
        >
          {copied ? <Check size={14} /> : <LinkIcon size={14} />}
          {copied ? 'Copied' : 'Share'}
        </button>

        <button
          onClick={() => exportRef.current?.exportPng()}
          className="flex items-center gap-1.5 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Download size={14} />
          Export
        </button>
      </div>
    </div>
    {status === 'disconnected' && (
      <div className="border-b border-amber-200 bg-amber-50 px-4 py-1.5 text-center text-xs text-amber-800">
        Can&apos;t connect to Liveblocks — real-time sync is off. Check that{' '}
        <code>VITE_LIVEBLOCKS_PUBLIC_KEY</code> is set to a valid key in{' '}
        <code>frontend/.env</code>, then reload.
      </div>
    )}
    </div>
  )
}

interface PresenceLike {
  name: string
}

function PresenceNameEditor({
  presence,
  updatePresence,
}: {
  presence: PresenceLike
  updatePresence: (patch: { name: string }) => void
}) {
  const [editingName, setEditingName] = useState(false)

  if (editingName) {
    return (
      <input
        autoFocus
        defaultValue={presence.name}
        onBlur={(e) => {
          const name = e.target.value.trim() || presence.name
          updatePresence({ name })
          setStoredName(name)
          setEditingName(false)
        }}
        onKeyDown={(e) => e.key === 'Enter' && e.currentTarget.blur()}
        className="w-32 rounded border border-neutral-300 px-2 py-1 text-sm"
      />
    )
  }

  return (
    <button
      onClick={() => setEditingName(true)}
      className="text-sm text-neutral-500 hover:text-neutral-800"
      title="Change your display name"
    >
      {presence.name}
    </button>
  )
}
