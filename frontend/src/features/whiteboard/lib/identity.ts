const NAME_KEY = 'syncboard:name'
const COLOR_KEY = 'syncboard:color'

const ADJECTIVES = ['Swift', 'Bright', 'Calm', 'Bold', 'Quiet', 'Clever', 'Sunny', 'Brave']
const ANIMALS = ['Otter', 'Falcon', 'Panda', 'Lynx', 'Heron', 'Fox', 'Wren', 'Ibis']
const COLORS = ['#f97316', '#22c55e', '#3b82f6', '#a855f7', '#ec4899', '#14b8a6', '#eab308', '#ef4444']

function randomFrom<T>(arr: T[]): T {
  return arr[Math.floor(Math.random() * arr.length)]
}

export function getStoredName(): string {
  if (typeof window === 'undefined') return 'Guest'
  const existing = window.localStorage.getItem(NAME_KEY)
  if (existing) return existing
  const name = `${randomFrom(ADJECTIVES)} ${randomFrom(ANIMALS)}`
  window.localStorage.setItem(NAME_KEY, name)
  return name
}

/**
 * Like `getStoredName`, but prefers the signed-in account's display
 * name. Only falls back to a locally stored/generated guest name when
 * there is no account (there always is one now that boards require
 * login, but this keeps the function safe to call without one).
 */
export function getInitialName(accountName?: string | null): string {
  if (accountName) return accountName
  return getStoredName()
}

export function setStoredName(name: string) {
  window.localStorage.setItem(NAME_KEY, name)
}

export function getStoredColor(): string {
  if (typeof window === 'undefined') return COLORS[0]
  const existing = window.localStorage.getItem(COLOR_KEY)
  if (existing) return existing
  const color = randomFrom(COLORS)
  window.localStorage.setItem(COLOR_KEY, color)
  return color
}
