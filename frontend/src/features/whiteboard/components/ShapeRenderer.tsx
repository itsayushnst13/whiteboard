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

export function ShapeRenderer({ shape, isSelected, draggable, onSelect, onDragEnd, onDblClick }: ShapeRendererProps) {
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
    onDragEnd: (e: Konva.KonvaEventObject<DragEvent>) => onDragEnd(e.target.x(), e.target.y()),
    stroke: isSelected ? '#2563eb' : shape.stroke,
    strokeWidth: isSelected ? shape.strokeWidth + 1 : shape.strokeWidth,
  }

  switch (shape.type) {
    case 'rectangle':
      return <Rect {...common} width={shape.width} height={shape.height} fill={shape.fill} cornerRadius={6} />
    case 'ellipse':
      return <Ellipse {...common} x={shape.x + shape.width / 2} y={shape.y + shape.height / 2} radiusX={Math.abs(shape.width) / 2} radiusY={Math.abs(shape.height) / 2} fill={shape.fill} />
    case 'star':
      return <Star {...common} x={shape.x + shape.width / 2} y={shape.y + shape.height / 2} numPoints={5} innerRadius={Math.min(Math.abs(shape.width), Math.abs(shape.height)) / 4} outerRadius={Math.min(Math.abs(shape.width), Math.abs(shape.height)) / 2} fill={shape.fill} />
    case 'line':
      return <Line {...common} points={shape.points} lineCap="round" lineJoin="round" hitStrokeWidth={16} />
    case 'arrow':
      return <Arrow {...common} points={shape.points} fill={shape.stroke} pointerLength={12} pointerWidth={12} hitStrokeWidth={16} />
    case 'pencil':
      return <Line {...common} points={shape.points} tension={0.4} lineCap="round" lineJoin="round" fill={undefined} hitStrokeWidth={16} />
    case 'text':
      return (
        <Text
          {...common}
          text={shape.text || ' '}
          fontSize={shape.fontSize}
          width={shape.width}
          height={44}
          padding={4}
          wrap="word"
          fill={shape.fill}
          stroke={undefined}
          hitStrokeWidth={12}
        />
      )
    case 'sticky':
      return (
        <>
          <Rect {...common} width={shape.width} height={shape.height} fill={shape.fill} cornerRadius={8} shadowColor="#0f172a" shadowOpacity={0.12} shadowBlur={12} shadowOffsetY={4} />
          <Text
            {...common}
            x={shape.x + 10}
            y={shape.y + 10}
            width={shape.width - 20}
            height={shape.height - 20}
            text={shape.text || ' '}
            fontSize={16}
            fill="#172033"
            stroke={undefined}
            listening={false}
          />
        </>
      )
    default:
      return null
  }
}
