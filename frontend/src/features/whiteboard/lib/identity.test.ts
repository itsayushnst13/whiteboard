import { beforeEach, describe, expect, it } from 'vitest'
import { getInitialName, getStoredName, setStoredName } from './identity'

describe('getInitialName', () => {
  beforeEach(() => {
    window.localStorage.clear()
  })

  it('uses the account name when no name has been stored yet', () => {
    expect(getInitialName('Ada Lovelace')).toBe('Ada Lovelace')
  })

  it('falls back to a generated guest name when there is no account name', () => {
    const name = getInitialName(undefined)
    expect(name.split(' ')).toHaveLength(2)
  })

  it('prefers the account name even over a previously stored guest name', () => {
    setStoredName('Stale Guest Name')
    expect(getInitialName('Ada Lovelace')).toBe('Ada Lovelace')
  })

  it('persists the generated guest name so it is stable across calls', () => {
    const first = getStoredName()
    const second = getStoredName()
    expect(first).toBe(second)
  })
})
