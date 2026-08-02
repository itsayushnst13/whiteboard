import { describe, expect, it } from 'vitest'
import { clampScale, isNegligibleShape, normalizeRect } from './geometry'

describe('clampScale', () => {
  it('clamps below the minimum', () => {
    expect(clampScale(0.01)).toBe(0.2)
  })
  it('clamps above the maximum', () => {
    expect(clampScale(10)).toBe(4)
  })
  it('passes through values in range', () => {
    expect(clampScale(1.5)).toBe(1.5)
  })
})

describe('normalizeRect', () => {
  it('normalizes a rect drawn top-left to bottom-right', () => {
    expect(normalizeRect({ x: 10, y: 10 }, { x: 50, y: 60 })).toEqual({
      x: 10,
      y: 10,
      width: 40,
      height: 50,
    })
  })
  it('normalizes a rect drawn bottom-right to top-left', () => {
    expect(normalizeRect({ x: 50, y: 60 }, { x: 10, y: 10 })).toEqual({
      x: 10,
      y: 10,
      width: 40,
      height: 50,
    })
  })
})

describe('isNegligibleShape', () => {
  it('flags shapes smaller than the threshold', () => {
    expect(isNegligibleShape(1, 1)).toBe(true)
  })
  it('does not flag shapes at or above the threshold', () => {
    expect(isNegligibleShape(5, 5)).toBe(false)
  })
})
