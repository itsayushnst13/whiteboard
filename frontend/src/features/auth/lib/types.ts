export interface AuthUser {
  id: number
  email: string
  display_name: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: AuthUser
}
