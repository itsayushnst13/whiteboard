import { Group, Label, Path, Tag, Text } from 'react-konva'
import type { Presence } from '../lib/liveblocks'

interface OtherUser {
  connectionId: number
  presence: Presence
}

export function Cursors({
  others,
}: {
  others: readonly OtherUser[]
  scale: number
  stagePos: { x: number; y: number }
}) {
  return (
    <>
      {others.map((other) => {
        const cursor = other.presence.cursor
        if (!cursor) return null
        const color = other.presence.color || '#3b82f6'
        return (
          <Group key={other.connectionId} x={cursor.x} y={cursor.y} listening={false}>
            <Path data="M0 0L0 16L4.5 12.5L7.5 19L10 18L7 11.5L12 11.5Z" fill={color} />
            <Label x={14} y={2}>
              <Tag fill={color} cornerRadius={4} />
              <Text
                text={other.presence.name || 'Guest'}
                fontSize={12}
                padding={4}
                fill="white"
              />
            </Label>
          </Group>
        )
      })}
    </>
  )
}
