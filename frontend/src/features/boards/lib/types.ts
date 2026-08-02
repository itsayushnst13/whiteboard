export type BoardRole = 'owner' | 'editor' | 'viewer'

export interface BoardSummary {
  id: number
  room_id: string
  name: string
  owner_id: number
  role: BoardRole
  created_at: string
  updated_at: string
}

export interface Collaborator {
  user_id: number
  email: string
  display_name: string
  role: Exclude<BoardRole, 'owner'>
  created_at: string
}
