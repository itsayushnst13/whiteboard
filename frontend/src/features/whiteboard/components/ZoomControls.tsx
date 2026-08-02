import { Maximize, Minus, Plus } from 'lucide-react'

interface ZoomControlsProps {
  scale: number
  onZoomIn: () => void
  onZoomOut: () => void
  onReset: () => void
}

export function ZoomControls({ scale, onZoomIn, onZoomOut, onReset }: ZoomControlsProps) {
  return (
    <div className="absolute bottom-4 left-4 z-10 flex items-center gap-1 rounded-xl border border-neutral-200 bg-white p-1 shadow-lg">
      <button
        onClick={onReset}
        title="Reset view"
        className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100"
      >
        <Maximize size={14} />
      </button>
      <button
        onClick={onZoomOut}
        title="Zoom out"
        className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100"
      >
        <Minus size={14} />
      </button>
      <span className="w-12 text-center text-xs text-neutral-500">{Math.round(scale * 100)}%</span>
      <button
        onClick={onZoomIn}
        title="Zoom in"
        className="flex h-8 w-8 items-center justify-center rounded-lg text-neutral-600 hover:bg-neutral-100"
      >
        <Plus size={14} />
      </button>
    </div>
  )
}
