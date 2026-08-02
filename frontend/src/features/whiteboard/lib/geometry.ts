export function clampScale(scale: number, min = 0.2, max = 4): number {
  return Math.min(max, Math.max(min, scale))
}

export function normalizeRect(
  start: { x: number; y: number },
  end: { x: number; y: number },
): { x: number; y: number; width: number; height: number } {
  return {
    x: Math.min(start.x, end.x),
    y: Math.min(start.y, end.y),
    width: Math.abs(end.x - start.x),
    height: Math.abs(end.y - start.y),
  }
}

export function isNegligibleShape(width: number, height: number, threshold = 3): boolean {
  return Math.abs(width) < threshold && Math.abs(height) < threshold
}

export function isDraftNegligible(shape: import('../types').Shape): boolean {
  switch (shape.type) {
    case 'pencil':
      return shape.points.length < 4
    case 'rectangle':
    case 'ellipse':
    case 'star':
      return isNegligibleShape(shape.width, shape.height)
    default:
      return false
  }
}
