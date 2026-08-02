import {
  ArrowUpRight,
  Eraser,
  Hand,
  Minus,
  MousePointer2,
  Pencil,
  Redo2,
  Square,
  StickyNote,
  Star as StarIcon,
  Type,
  Undo2,
  Circle,
  Trash2,
} from 'lucide-react'
import clsx from 'clsx'
import type { Tool } from '../types'
import { useCanRedo, useCanUndo, useHistory } from '../lib/liveblocks'

interface ToolbarProps {
  tool: Tool
  onToolChange: (tool: Tool) => void
  onClearBoard: () => void
  disabled?: boolean
  disabledReason?: string
}

const TOOLS: { tool: Tool; icon: typeof MousePointer2; label: string }[] = [
  { tool: 'select', icon: MousePointer2, label: 'Select (V)' },
  { tool: 'hand', icon: Hand, label: 'Pan (H)' },
  { tool: 'pencil', icon: Pencil, label: 'Draw (P)' },
  { tool: 'eraser', icon: Eraser, label: 'Erase (E)' },
  { tool: 'rectangle', icon: Square, label: 'Rectangle (R)' },
  { tool: 'ellipse', icon: Circle, label: 'Ellipse (O)' },
  { tool: 'line', icon: Minus, label: 'Line (L)' },
  { tool: 'arrow', icon: ArrowUpRight, label: 'Arrow (A)' },
  { tool: 'star', icon: StarIcon, label: 'Star (S)' },
  { tool: 'text', icon: Type, label: 'Text (T)' },
  { tool: 'sticky', icon: StickyNote, label: 'Sticky note (N)' },
]

export function Toolbar({
  tool,
  onToolChange,
  onClearBoard,
  disabled = false,
  disabledReason,
}: ToolbarProps) {
  const history = useHistory()
  const canUndo = useCanUndo()
  const canRedo = useCanRedo()

  return (
    <div
      title={disabled ? (disabledReason ?? 'Connecting to the board…') : undefined}
      className={clsx(
        'absolute left-4 top-1/2 z-10 flex -translate-y-1/2 flex-col gap-1 rounded-2xl border border-neutral-200 bg-white p-2 shadow-lg transition-opacity',
        disabled && 'pointer-events-none opacity-40',
      )}
    >
      {TOOLS.map(({ tool: t, icon: Icon, label }) => (
        <button
          key={t}
          title={label}
          onClick={() => onToolChange(t)}
          className={clsx(
            'flex h-9 w-9 items-center justify-center rounded-lg transition-colors',
            tool === t ? 'bg-blue-100 text-blue-600' : 'text-neutral-600 hover:bg-neutral-100',
          )}
        >
          <Icon size={18} />
        </button>
      ))}
      <div className="my-1 border-t border-neutral-200" />
      <button
        title="Undo (Ctrl+Z)"
        disabled={disabled || !canUndo}
        onClick={() => history.undo()}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100 disabled:opacity-30"
      >
        <Undo2 size={18} />
      </button>
      <button
        title="Redo (Ctrl+Shift+Z)"
        disabled={disabled || !canRedo}
        onClick={() => history.redo()}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100 disabled:opacity-30"
      >
        <Redo2 size={18} />
      </button>
      <button
        title="Clear board"
        disabled={disabled}
        onClick={() => {
          if (window.confirm('Clear the entire board for everyone?')) onClearBoard()
        }}
        className="flex h-9 w-9 items-center justify-center rounded-lg text-neutral-600 hover:bg-red-50 hover:text-red-600"
      >
        <Trash2 size={18} />
      </button>
    </div>
  )
}
