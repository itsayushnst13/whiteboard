import { Arrow, Ellipse, Line, Rect, Star, Text } from 'react-konva'
import type Konva from 'konva'
import type { Shape } from '../types'

interface ShapeRendererProps {
  shape: Shape
  isSelected: boolean
  draggable: boolean
  onSelect: () => void
  onDragEnd: (x: number, y: number) => void
  onDblClick?: () => void
}

export function ShapeRenderer({
  shape,
  isSelected,
  draggable,
  onSelect,
  onDragEnd,
  onDblClick,
}: ShapeRendererProps) {
  const common = {
    id: shape.id,
    x: shape.x,
    y: shape.y,
    rotation: shape.rotation,
    draggable,
    onClick: onSelect,
    onTap: onSelect,
    onDblClick,
    onDblTap: onDblClick,
    onDragEnd: (e: Konva.KonvaEventObject<DragEvent>) => {
      onDragEnd(e.target.x(), e.target.y())
    },
    stroke: isSelected ? '#3b82f6' : shape.stroke,
    strokeWidth: isSelected ? shape.strokeWidth + 1 : shape.strokeWidth,
  }

  switch (shape.type) {
    case 'rectangle':
      return (
        <Rect
          {...common}
          width={shape.width}
          height={shape.height}
          fill={shape.fill}
          cornerRadius={4}
        />
      )
    case 'ellipse':
      return (
        <Ellipse
          {...common}
          x={shape.x + shape.width / 2}
          y={shape.y + shape.height / 2}
          radiusX={Math.abs(shape.width) / 2}
          radiusY={Math.abs(shape.height) / 2}
          fill={shape.fill}
        />
      )
    case 'star':
      return (
        <Star
          {...common}
          x={shape.x + shape.width / 2}
          y={shape.y + shape.height / 2}
          numPoints={5}
          innerRadius={Math.min(Math.abs(shape.width), Math.abs(shape.height)) / 4}
          outerRadius={Math.min(Math.abs(shape.width), Math.abs(shape.height)) / 2}
          fill={shape.fill}
        />
      )
    case 'line':
      return (
        <Line
          {...common}
          points={shape.points}
          lineCap="round"
          lineJoin="round"
          hitStrokeWidth={16}
        />
      )
    case 'arrow':
      return (
        <Arrow
          {...common}
          points={shape.points}
          fill={shape.stroke}
          pointerLength={12}
          pointerWidth={12}
          hitStrokeWidth={16}
        />
      )
    case 'pencil':
      return (
        <Line
          {...common}
          points={shape.points}
          tension={0.4}
          lineCap="round"
          lineJoin="round"
          fill={undefined}
          hitStrokeWidth={16}
        />
      )
    case 'text':
      return (
        <Text
          {...common}
          text={shape.text}
          fontSize={shape.fontSize}
          width={shape.width}
          fill={shape.fill}
          stroke={undefined}
        />
      )
    case 'sticky':
      return (
        <>
          <Rect
            {...common}
            width={shape.width}
            height={shape.height}
            fill={shape.fill}
            cornerRadius={2}
            shadowColor="black"
            shadowOpacity={0.15}
            shadowBlur={6}
            shadowOffsetY={3}
          />
          <Text
            x={shape.x + 10}
            y={shape.y + 10}
            width={shape.width - 20}
            height={shape.height - 20}
            text={shape.text}
            fontSize={16}
            fill="#1e1e1e"
            listening={false}
          />
        </>
      )
    default:
      return null
  }
}
