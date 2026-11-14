import { useEffect, useRef, useState } from 'react'
import type { Shape } from '../types'

interface TextEditorOverlayProps {
  shape: Shape
  scale: number
  stagePos: { x: number; y: number }
  onChange: (text: string) => void
  onClose: () => void
}

export function TextEditorOverlay({ shape, scale, stagePos, onChange, onClose }: TextEditorOverlayProps) {
  const ref = useRef<HTMLTextAreaElement>(null)
  const [value, setValue] = useState(shape.text)

  useEffect(() => {
    ref.current?.focus()
    ref.current?.setSelectionRange(value.length, value.length)
  }, [])

  if (shape.type !== 'text' && shape.type !== 'sticky') return null

  const isSticky = shape.type === 'sticky'
  const width = isSticky ? shape.width - 20 : shape.width
  const height = isSticky ? shape.height - 20 : 44
  const fontSize = isSticky ? 16 : shape.fontSize

  function commit() {
    onChange(value)
    onClose()
  }

  return (
    <textarea
      ref={ref}
      aria-label={isSticky ? 'Edit sticky note' : 'Edit text'}
      value={value}
      onChange={(event) => setValue(event.target.value)}
      onBlur={commit}
      onKeyDown={(event) => {
        if (event.key === 'Escape') {
          event.preventDefault()
          event.currentTarget.blur()
        }
        if (event.key === 'Enter' && !event.shiftKey && !isSticky) {
          event.preventDefault()
          event.currentTarget.blur()
        }
      }}
      onPointerDown={(event) => event.stopPropagation()}
      onClick={(event) => event.stopPropagation()}
      style={{
        position: 'absolute',
        top: shape.y * scale + stagePos.y + (isSticky ? 10 * scale : 0),
        left: shape.x * scale + stagePos.x + (isSticky ? 10 * scale : 0),
        width: Math.max(40, width * scale),
        minHeight: Math.max(36, height * scale),
        height: isSticky ? Math.max(40, height * scale) : undefined,
        fontSize: Math.max(10, fontSize * scale),
        lineHeight: 1.35,
        border: '2px solid #2563eb',
        borderRadius: 8,
        padding: 6,
        background: isSticky ? 'rgba(255,255,255,0.25)' : 'rgba(255,255,255,0.96)',
        boxShadow: '0 8px 24px rgba(15,23,42,0.12)',
        resize: 'both',
        outline: 'none',
        fontFamily: 'inherit',
        fontWeight: 500,
        color: '#172033',
        zIndex: 50,
      }}
    />
  )
}
