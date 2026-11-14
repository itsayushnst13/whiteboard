import {
  ArrowUpRight, Eraser, Hand, Minus, MousePointer2, Pencil, Redo2,
  Square, StickyNote, Star as StarIcon, Type, Undo2, Circle, Trash2,
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

const TOOLS: { tool: Tool; icon: typeof MousePointer2; label: string; shortcut: string }[] = [
  { tool: 'select', icon: MousePointer2, label: 'Select', shortcut: 'V' },
  { tool: 'hand', icon: Hand, label: 'Pan canvas', shortcut: 'H' },
  { tool: 'pencil', icon: Pencil, label: 'Pen', shortcut: 'P' },
  { tool: 'eraser', icon: Eraser, label: 'Eraser', shortcut: 'E' },
  { tool: 'rectangle', icon: Square, label: 'Rectangle', shortcut: 'R' },
  { tool: 'ellipse', icon: Circle, label: 'Ellipse', shortcut: 'O' },
  { tool: 'line', icon: Minus, label: 'Line', shortcut: 'L' },
  { tool: 'arrow', icon: ArrowUpRight, label: 'Arrow', shortcut: 'A' },
  { tool: 'star', icon: StarIcon, label: 'Star', shortcut: 'S' },
  { tool: 'text', icon: Type, label: 'Text', shortcut: 'T' },
  { tool: 'sticky', icon: StickyNote, label: 'Sticky note', shortcut: 'N' },
]

export function Toolbar({ tool, onToolChange, onClearBoard, disabled = false, disabledReason }: ToolbarProps) {
  const history = useHistory()
  const canUndo = useCanUndo()
  const canRedo = useCanRedo()

  return (
    <div
      title={disabled ? (disabledReason ?? 'Connecting to the board…') : undefined}
      aria-label="Whiteboard tools"
      className={clsx(
        'absolute left-5 top-1/2 z-30 flex max-h-[calc(100vh-7rem)] -translate-y-1/2 flex-col items-center gap-1 overflow-y-auto rounded-2xl border border-slate-200/80 bg-white/95 p-2 shadow-[0_12px_40px_-12px_rgba(15,23,42,0.28)] backdrop-blur-xl transition-all',
        disabled && 'pointer-events-none opacity-45',
      )}
    >
      <div className="mb-1 px-2 py-1 text-[9px] font-bold uppercase tracking-[0.18em] text-slate-400">Tools</div>
      {TOOLS.map(({ tool: current, icon: Icon, label, shortcut }) => (
        <button
          key={current}
          type="button"
          title={`${label} · ${shortcut}`}
          aria-label={label}
          aria-pressed={tool === current}
          onClick={() => onToolChange(current)}
          className={clsx(
            'group relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-all duration-150',
            tool === current
              ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
              : 'text-slate-500 hover:bg-slate-100 hover:text-slate-900',
          )}
        >
          <Icon size={18} strokeWidth={2} />
          <span className="pointer-events-none absolute left-12 z-50 whitespace-nowrap rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg transition-opacity group-hover:opacity-100">
            {label}<span className="ml-2 text-slate-400">{shortcut}</span>
          </span>
        </button>
      ))}
      <div className="my-1 h-px w-8 shrink-0 bg-slate-200" />
      <button type="button" title="Undo · Ctrl/⌘ Z" aria-label="Undo" disabled={disabled || !canUndo} onClick={() => history.undo()} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-25">
        <Undo2 size={18} />
      </button>
      <button type="button" title="Redo · Ctrl/⌘ Shift Z" aria-label="Redo" disabled={disabled || !canRedo} onClick={() => history.redo()} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-slate-500 transition hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-25">
        <Redo2 size={18} />
      </button>
      <div className="my-1 h-px w-8 shrink-0 bg-slate-200" />
      <button type="button" title="Clear board" aria-label="Clear board" disabled={disabled} onClick={() => { if (window.confirm('Clear the entire board for everyone?')) onClearBoard() }} className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-slate-400 transition hover:bg-red-50 hover:text-red-600 disabled:opacity-25">
        <Trash2 size={18} />
      </button>
    </div>
  )
}
