import { useCallback, useEffect, useRef, useState } from 'react'
import { Layer, Stage } from 'react-konva'
import type Konva from 'konva'
import { nanoid } from 'nanoid'
import {
  useHistory,
  useMutation,
  useMyPresence,
  useOthers,
  useStorage,
} from '../lib/liveblocks'
import type { Shape, ShapeType, Tool } from '../types'
import { STICKY_COLORS } from '../types'
import { ShapeRenderer } from './ShapeRenderer'
import { Cursors } from './Cursors'
import { TextEditorOverlay } from './TextEditorOverlay'
import { Toolbar } from './Toolbar'
import { ZoomControls } from './ZoomControls'
import { clampScale, isDraftNegligible, normalizeRect } from '../lib/geometry'

const DRAW_TOOLS: ShapeType[] = ['rectangle', 'ellipse', 'star']
const LINE_TOOLS: ShapeType[] = ['line', 'arrow']

function pointerPosition(stage: Konva.Stage | null): { x: number; y: number } | null {
  if (!stage) return null
  const pos = stage.getPointerPosition()
  if (!pos) return null
  const transform = stage.getAbsoluteTransform().copy().invert()
  return transform.point(pos)
}

export interface BoardHandle {
  exportPng: () => void
}

export function Board({ exportRef }: { exportRef: React.MutableRefObject<BoardHandle | null> }) {
  const stageRef = useRef<Konva.Stage>(null)
  const shapes = useStorage((root) => root.shapes)
  const [presence, updatePresence] = useMyPresence()
  const others = useOthers()
  const history = useHistory()

  const [tool, setTool] = useState<Tool>('select')
  const [scale, setScale] = useState(1)
  const [stagePos, setStagePos] = useState({ x: 0, y: 0 })
  const [draft, setDraftState] = useState<Shape | null>(null)
  const draftRef = useRef<Shape | null>(null)
  const setDraft = useCallback((updater: Shape | null | ((prev: Shape | null) => Shape | null)) => {
    setDraftState((prev) => {
      const next = typeof updater === 'function' ? (updater as (p: Shape | null) => Shape | null)(prev) : updater
      draftRef.current = next
      return next
    })
  }, [])
  const [editingShapeId, setEditingShapeId] = useState<string | null>(null)
  const isDrawing = useRef(false);
  const isErasing = useRef(false)
  const drawStart = useRef({ x: 0, y: 0 })
  const storageReady = shapes !== null

  const addShape = useMutation(({ storage, self: mSelf }, shape: Shape) => {
    storage.get('shapes').set(shape.id, { ...shape, authorId: mSelf.connectionId.toString() })
  }, [])

  const updateShapePosition = useMutation(({ storage }, id: string, x: number, y: number) => {
    const shape = storage.get('shapes').get(id)
    if (shape) storage.get('shapes').set(id, { ...shape, x, y })
  }, [])

  const updateShapeText = useMutation(({ storage }, id: string, text: string) => {
    const shape = storage.get('shapes').get(id)
    if (shape && 'text' in shape) storage.get('shapes').set(id, { ...shape, text })
  }, [])

  const deleteShape = useMutation(({ storage }, id: string) => {
    storage.get('shapes').delete(id)
  }, [])

  const eraseAt = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent | TouchEvent>) => {
      const target = e.target
      if (!target || target === stageRef.current) return
      const id = target.id()
      if (id) deleteShape(id)
    },
    [deleteShape],
  )

  const clearBoard = useMutation(({ storage }) => {
    const map = storage.get('shapes')
    Array.from(map.keys()).forEach((key) => map.delete(key))
  }, [])

  const shapeList: Shape[] = shapes ? (Object.values(shapes) as Shape[]) : []

  const selectedShapeId = presence.selectedShapeId
  const setSelectedShapeId = (id: string | null) => updatePresence({ selectedShapeId: id })

  const strokeColor = '#1e1e1e'
  const fillFor = (type: ShapeType) =>
    type === 'sticky'
      ? STICKY_COLORS[Math.floor(Math.random() * STICKY_COLORS.length)]
      : type === 'text'
        ? '#1e1e1e'
        : 'transparent'

  const handleMouseDown = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent | TouchEvent>) => {
      const stage = stageRef.current
      const pos = pointerPosition(stage)
      if (!pos) return

      if (tool === 'select' || tool === 'hand') {
        if (e.target === stage) setSelectedShapeId(null)
        return
      }

      if (!storageReady) return

      if (tool === 'eraser') {
        isErasing.current = true
        eraseAt(e)
        return
      }

      if (tool === 'text' || tool === 'sticky') {
        const id = nanoid()
        const shape: Shape =
          tool === 'text'
            ? {
                id,
                type: 'text',
                x: pos.x,
                y: pos.y,
                rotation: 0,
                fill: '#1e1e1e',
                stroke: 'transparent',
                strokeWidth: 0,
                authorId: '',
                text: '',
                fontSize: 20,
                width: 240,
              }
            : {
                id,
                type: 'sticky',
                x: pos.x,
                y: pos.y,
                rotation: 0,
                fill: fillFor('sticky'),
                stroke: 'transparent',
                strokeWidth: 0,
                authorId: '',
                text: '',
                width: 180,
                height: 160,
              }
        addShape(shape)
        setEditingShapeId(id)
        setTool('select')
        return
      }

      isDrawing.current = true
      drawStart.current = pos

      if (tool === 'pencil') {
        setDraft({
          id: nanoid(),
          type: 'pencil',
          x: 0,
          y: 0,
          rotation: 0,
          fill: 'transparent',
          stroke: strokeColor,
          strokeWidth: 3,
          authorId: '',
          points: [pos.x, pos.y],
        })
        return
      }

      if (DRAW_TOOLS.includes(tool as ShapeType)) {
        setDraft({
          id: nanoid(),
          type: tool as ShapeType,
          x: pos.x,
          y: pos.y,
          width: 0,
          height: 0,
          rotation: 0,
          fill: 'transparent',
          stroke: strokeColor,
          strokeWidth: 2,
          authorId: '',
        } as Shape)
        return
      }

      if (LINE_TOOLS.includes(tool as ShapeType)) {
        setDraft({
          id: nanoid(),
          type: tool as ShapeType,
          x: 0,
          y: 0,
          rotation: 0,
          fill: 'transparent',
          stroke: strokeColor,
          strokeWidth: 2,
          authorId: '',
          points: [pos.x, pos.y, pos.x, pos.y],
        } as Shape)
      }
    },
    [tool, addShape, eraseAt, storageReady],
  )

  const handleMouseMove = useCallback(
    (e: Konva.KonvaEventObject<MouseEvent | TouchEvent>) => {
      const stage = stageRef.current
      const pos = pointerPosition(stage)
      if (pos) updatePresence({ cursor: pos })

      if (isErasing.current) {
        eraseAt(e)
        return
      }

      if (!isDrawing.current || !pos) return

      setDraft((prev) => {
        if (!prev) return prev
        if (prev.type === 'pencil') {
          return { ...prev, points: [...prev.points, pos.x, pos.y] }
        }
        if (DRAW_TOOLS.includes(prev.type)) {
          const rect = normalizeRect(drawStart.current, pos)
          return { ...prev, ...rect } as Shape
        }
        if (LINE_TOOLS.includes(prev.type)) {
          const start = drawStart.current
          return { ...prev, points: [start.x, start.y, pos.x, pos.y] } as Shape
        }
        return prev
      })
    },
    [updatePresence, eraseAt],
  )

  const handleMouseUp = useCallback(() => {
    isDrawing.current = false
    isErasing.current = false
    const finished = draftRef.current
    setDraft(null)
    if (finished && storageReady && !isDraftNegligible(finished)) {
      addShape(finished)
    }
  }, [addShape, storageReady])

  const handleWheel = useCallback((e: Konva.KonvaEventObject<WheelEvent>) => {
    e.evt.preventDefault()
    const stage = stageRef.current
    if (!stage) return
    const oldScale = scale
    const pointer = stage.getPointerPosition()
    if (!pointer) return
    const mousePointTo = {
      x: (pointer.x - stagePos.x) / oldScale,
      y: (pointer.y - stagePos.y) / oldScale,
    }
    const direction = e.evt.deltaY > 0 ? -1 : 1
    const newScale = clampScale(oldScale * (1 + direction * 0.05))
    setScale(newScale)
    setStagePos({
      x: pointer.x - mousePointTo.x * newScale,
      y: pointer.y - mousePointTo.y * newScale,
    })
  }, [scale, stagePos])

  useEffect(() => {
    updatePresence({ selectedTool: tool })
  }, [tool, updatePresence])

  useEffect(() => {
    function onKeyDown(ev: KeyboardEvent) {
      const target = ev.target as HTMLElement
      if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') return
      if (!storageReady) return
      if ((ev.key === 'Delete' || ev.key === 'Backspace') && selectedShapeId) {
        deleteShape(selectedShapeId)
        setSelectedShapeId(null)
      }
      if ((ev.metaKey || ev.ctrlKey) && ev.key === 'z' && !ev.shiftKey) {
        ev.preventDefault()
        history.undo()
      }
      if ((ev.metaKey || ev.ctrlKey) && (ev.key === 'y' || (ev.key === 'z' && ev.shiftKey))) {
        ev.preventDefault()
        history.redo()
      }
    }
    window.addEventListener('keydown', onKeyDown)
    return () => window.removeEventListener('keydown', onKeyDown)
  }, [selectedShapeId, deleteShape, history, storageReady])

  exportRef.current = {
    exportPng: () => {
      const stage = stageRef.current
      if (!stage) return
      const uri = stage.toDataURL({ pixelRatio: 2 })
      const link = document.createElement('a')
      link.download = 'syncboard-export.png'
      link.href = uri
      link.click()
    },
  }

  const editingShape = editingShapeId ? shapeList.find((s) => s.id === editingShapeId) : null

  return (
    <div className="relative h-full w-full overflow-hidden bg-neutral-50">
      <Toolbar
        tool={tool}
        onToolChange={setTool}
        onClearBoard={clearBoard}
        disabled={!storageReady}
      />
      <Stage
        ref={stageRef}
        width={window.innerWidth}
        height={window.innerHeight}
        x={stagePos.x}
        y={stagePos.y}
        scaleX={scale}
        scaleY={scale}
        draggable={tool === 'hand'}
        onDragEnd={(e) => {
          if (tool === 'hand') setStagePos({ x: e.target.x(), y: e.target.y() })
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onTouchStart={handleMouseDown}
        onTouchMove={handleMouseMove}
        onTouchEnd={handleMouseUp}
        onWheel={handleWheel}
        className={
          tool === 'hand'
            ? 'cursor-grab'
            : tool === 'select'
              ? 'cursor-default'
              : 'cursor-crosshair'
        }
      >
        <Layer>
          {shapeList.map((shape) => (
            <ShapeRenderer
              key={shape.id}
              shape={shape}
              isSelected={selectedShapeId === shape.id}
              draggable={tool === 'select'}
              onSelect={() => tool === 'eraser' ? deleteShape(shape.id) : setSelectedShapeId(shape.id)}
              onDragEnd={(x, y) => updateShapePosition(shape.id, x, y)}
              onDblClick={() =>
                (shape.type === 'text' || shape.type === 'sticky') && setEditingShapeId(shape.id)
              }
            />
          ))}
          {draft && (
            <ShapeRenderer
              shape={draft}
              isSelected={false}
              draggable={false}
              onSelect={() => {}}
              onDragEnd={() => {}}
            />
          )}
        </Layer>
        <Layer listening={false}>
          <Cursors others={others} scale={scale} stagePos={stagePos} />
        </Layer>
      </Stage>

      {editingShape && (
        <TextEditorOverlay
          shape={editingShape}
          scale={scale}
          stagePos={stagePos}
          onChange={(text) => updateShapeText(editingShape.id, text)}
          onClose={() => setEditingShapeId(null)}
        />
      )}

      <ZoomControls
        scale={scale}
        onZoomIn={() => setScale((s) => Math.min(4, s * 1.2))}
        onZoomOut={() => setScale((s) => Math.max(0.2, s / 1.2))}
        onReset={() => {
          setScale(1)
          setStagePos({ x: 0, y: 0 })
        }}
      />

    </div>
  )
}
