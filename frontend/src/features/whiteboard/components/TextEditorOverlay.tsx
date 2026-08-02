import { useEffect, useRef } from 'react'
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

  useEffect(() => {
    ref.current?.focus()
    ref.current?.select()
  }, [])

  if (shape.type !== 'text' && shape.type !== 'sticky') return null

  const width = shape.type === 'text' ? shape.width : shape.width - 20
  const height = shape.type === 'sticky' ? shape.height - 20 : 40
  const fontSize = shape.type === 'text' ? shape.fontSize : 16

  return (
    <textarea
      ref={ref}
      defaultValue={shape.text}
      onBlur={(e) => {
        onChange(e.target.value)
        onClose()
      }}
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          e.currentTarget.blur()
        }
        if (e.key === 'Enter' && !e.shiftKey && shape.type === 'text') {
          e.preventDefault()
          e.currentTarget.blur()
        }
      }}
      style={{
        position: 'absolute',
        top: shape.y * scale + stagePos.y + (shape.type === 'sticky' ? 10 * scale : 0),
        left: shape.x * scale + stagePos.x + (shape.type === 'sticky' ? 10 * scale : 0),
        width: width * scale,
        height: height * scale,
        fontSize: fontSize * scale,
        lineHeight: 1.3,
        border: '2px solid #3b82f6',
        borderRadius: 4,
        padding: 4,
        background: shape.type === 'sticky' ? 'transparent' : 'white',
        resize: 'none',
        outline: 'none',
        fontFamily: 'inherit',
        color: '#1e1e1e',
        zIndex: 50,
      }}
    />
  )
}
