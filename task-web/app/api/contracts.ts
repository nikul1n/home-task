// Mirrors the inspected Pydantic schemas. Compare with generated OpenAPI on API changes.
export type UUID = string;
export type TaskStatus = "todo" | "in_progress" | "done" | "cancelled";
export type ManualStatus = Exclude<TaskStatus, "done">;
export type Importance = "low" | "medium" | "high" | "critical";
export type MemberRole = "owner" | "admin" | "member" | "viewer";
export interface Credentials {
  email: string;
  password: string;
}
export interface UserCreate extends Credentials {
  name: string;
  phone: string;
  birthday: string | null;
  timezone: string;
}
export interface User extends Omit<UserCreate, "password"> {
  id: UUID;
  is_active: boolean;
  avatar_url: string | null;
}
export interface UserShort {
  id: UUID;
  username: string;
  name: string;
  avatar_url: string | null;
}
export interface Token {
  access_token: string;
  token_type: string;
}
export interface BoardCreate {
  title: string;
  description?: string | null;
}
export interface Board extends BoardCreate {
  id: UUID;
  creator_id: UUID;
  created_at: string;
  updated_at: string;
}
export interface BoardUpdate {
  title?: string | null;
  description?: string | null;
}
export interface MemberCreate {
  user_id: UUID;
  role?: Exclude<MemberRole, "owner">;
}
export interface Member {
  id: UUID;
  board_id: UUID;
  user_id: UUID;
  role: MemberRole;
  joined_at: string;
}
export interface TaskCreate {
  title: string;
  description?: string | null;
  importance?: Importance;
  deadline?: string | null;
  responsible_id?: UUID | null;
}
export interface TaskUpdate {
  title?: string | null;
  description?: string | null;
  importance?: Importance | null;
  deadline?: string | null;
  responsible_id?: UUID | null;
  status?: ManualStatus | null;
}
export interface Task extends TaskCreate {
  id: UUID;
  board_id: UUID;
  creator_id: UUID;
  status: TaskStatus;
  importance: Importance;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}
export interface TaskDetail extends Task {
  creator: UserShort;
  responsible: UserShort | null;
}
export interface TaskList {
  items: Task[];
  total: number | null;
  limit: number;
  offset: number;
}
export interface TaskFilters {
  status?: TaskStatus;
  importance?: Importance;
  responsible_id?: UUID;
  search?: string;
  limit?: number;
  offset?: number;
}
