import { createClient, LiveMap } from '@liveblocks/client'
import { createRoomContext } from '@liveblocks/react'
import type { Shape } from '../types'

const publicApiKey = import.meta.env.VITE_LIVEBLOCKS_PUBLIC_KEY as string | undefined

if (!publicApiKey) {
  // eslint-disable-next-line no-console
  console.warn(
    '[SyncBoard] VITE_LIVEBLOCKS_PUBLIC_KEY is not set. Copy frontend/.env.example to ' +
      'frontend/.env and add a public key from https://liveblocks.io/dashboard/apikeys ' +
      'to enable real-time collaboration.',
  )
}

export const client = createClient({
  publicApiKey: publicApiKey ?? 'pk_dev_missing_key',
  throttle: 16,
})

export type Presence = {
  cursor: { x: number; y: number } | null
  selectedTool: string
  selectedShapeId: string | null
  name: string
  color: string
}

export type Storage = {
  shapes: LiveMap<string, Shape>
}

export const {
  RoomProvider,
  useRoom,
  useMyPresence,
  useUpdateMyPresence,
  useOthers,
  useOthersMapped,
  useSelf,
  useStorage,
  useMutation,
  useHistory,
  useCanUndo,
  useCanRedo,
  useStatus,
} = createRoomContext<Presence, Storage>(client)
