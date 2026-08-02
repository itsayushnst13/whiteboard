import type { Json } from '@liveblocks/client'

export type Tool =
  | 'select'
  | 'hand'
  | 'pencil'
  | 'eraser'
  | 'rectangle'
  | 'ellipse'
  | 'arrow'
  | 'line'
  | 'star'
  | 'text'
  | 'sticky'

export type ShapeType =
  | 'rectangle'
  | 'ellipse'
  | 'arrow'
  | 'line'
  | 'star'
  | 'pencil'
  | 'text'
  | 'sticky'

interface Indexable {
  [key: string]: Json
}

export interface BaseShape extends Indexable {
  id: string
  type: ShapeType
  x: number
  y: number
  rotation: number
  fill: string
  stroke: string
  strokeWidth: number
  authorId: string
}

export interface RectShape extends BaseShape {
  type: 'rectangle'
  width: number
  height: number
}

export interface EllipseShape extends BaseShape {
  type: 'ellipse'
  width: number
  height: number
}

export interface StarShape extends BaseShape {
  type: 'star'
  width: number
  height: number
}

export interface LineShape extends BaseShape {
  type: 'line'
  points: number[]
}

export interface ArrowShape extends BaseShape {
  type: 'arrow'
  points: number[]
}

export interface PencilShape extends BaseShape {
  type: 'pencil'
  points: number[]
}

export interface TextShape extends BaseShape {
  type: 'text'
  text: string
  fontSize: number
  width: number
}

export interface StickyShape extends BaseShape {
  type: 'sticky'
  text: string
  width: number
  height: number
}

export type Shape =
  | RectShape
  | EllipseShape
  | StarShape
  | LineShape
  | ArrowShape
  | PencilShape
  | TextShape
  | StickyShape

export const STICKY_COLORS = ['#fef08a', '#fecdd3', '#bbf7d0', '#bfdbfe', '#e9d5ff', '#fed7aa']

export const SHAPE_STROKE_COLORS = [
  '#1e1e1e',
  '#e03131',
  '#2f9e44',
  '#1971c2',
  '#f08c00',
]
