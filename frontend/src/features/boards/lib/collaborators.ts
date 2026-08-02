import { api } from '../../../lib/api'
import type { BoardRole, Collaborator } from './types'

type ShareableRole = Exclude<BoardRole, 'owner'>

/** Invite (or update the role of) a collaborator by email. Owner only. */
export function shareBoard(boardId: number, email: string, role: ShareableRole): Promise<Collaborator> {
  return api.post<Collaborator>(`/boards/${boardId}/share`, { email, role })
}

export function listCollaborators(boardId: number): Promise<Collaborator[]> {
  return api.get<Collaborator[]>(`/boards/${boardId}/collaborators`)
}

export function removeCollaborator(boardId: number, userId: number): Promise<void> {
  return api.delete(`/boards/${boardId}/collaborators/${userId}`)
}
