import { LiveMap } from '@liveblocks/client'
import { ClientSideSuspense } from '@liveblocks/react'
import { useRef } from 'react'
import { RoomProvider } from '../lib/liveblocks'
import { getInitialName, getStoredColor } from '../lib/identity'
import { ErrorBoundary } from './ErrorBoundary'
import { Board, type BoardHandle } from './Board'
import { TopBar } from './TopBar'
import type { BoardRole } from '../../boards/lib/types'

function BoardLoading() {
  return (
    <div className="flex h-screen w-screen items-center justify-center bg-neutral-50 text-sm text-neutral-400">
      Connecting to board…
    </div>
  )
}

interface BoardPageProps {
  roomId: string
  boardId: number
  boardName: string
  role: BoardRole
  accountName?: string | null
  onRenameBoard: (name: string) => Promise<void>
}

export function BoardPage({
  roomId,
  boardId,
  boardName,
  role,
  accountName,
  onRenameBoard,
}: BoardPageProps) {
  const exportRef = useRef<BoardHandle | null>(null)
  const readOnly = role === 'viewer'

  return (
    <ErrorBoundary>
      <RoomProvider
        id={roomId}
        initialPresence={{
          cursor: null,
          selectedTool: 'select',
          selectedShapeId: null,
          name: getInitialName(accountName),
          color: getStoredColor(),
        }}
        initialStorage={{
          shapes: new LiveMap(),
        }}
      >
        <ClientSideSuspense fallback={<BoardLoading />}>
          <div className="relative h-screen w-screen overflow-hidden">
            <TopBar
              boardId={boardId}
              boardName={boardName}
              role={role}
              onRenameBoard={onRenameBoard}
              exportRef={exportRef}
            />
            <Board exportRef={exportRef} readOnly={readOnly} />
          </div>
        </ClientSideSuspense>
      </RoomProvider>
    </ErrorBoundary>
  )
}
