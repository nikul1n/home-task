import { http } from "./client";
import type {
  Board,
  BoardCreate,
  BoardUpdate,
  Credentials,
  ManualStatus,
  Member,
  MemberCreate,
  Task,
  TaskCreate,
  TaskDetail,
  TaskFilters,
  TaskList,
  TaskUpdate,
  Token,
  User,
  UserCreate,
} from "./contracts";

const taskPath = (boardId: string, taskId?: string) =>
  `/boards/${encodeURIComponent(boardId)}/tasks${taskId ? `/${encodeURIComponent(taskId)}` : ""}`;
const boardPath = (id: string) => `/boards/${encodeURIComponent(id)}`;
export const authApi = {
  login: async (data: Credentials) =>
    (await http.post<Token>("/auth/login", data)).data,
  register: async (data: UserCreate) =>
    (await http.post<User>("/auth/registration", data)).data,
  me: async (signal?: AbortSignal) =>
    (await http.get<User>("/users/me", { signal })).data,
};
export const boardsApi = {
  list: async (signal?: AbortSignal) =>
    (await http.get<Board[]>("/boards/", { signal })).data,
  get: async (id: string, signal?: AbortSignal) =>
    (await http.get<Board>(boardPath(id), { signal })).data,
  create: async (data: BoardCreate) =>
    (await http.post<Board>("/boards/create_board", data)).data,
  update: async (id: string, data: BoardUpdate) =>
    (await http.patch<Board>(boardPath(id), data)).data,
  remove: async (id: string) => {
    await http.delete(boardPath(id));
  },
  addMember: async (id: string, data: MemberCreate) =>
    (await http.post<Member>(`${boardPath(id)}/members`, data)).data,
};
export const tasksApi = {
  list: async (
    boardId: string,
    filters: TaskFilters = {},
    signal?: AbortSignal,
  ) =>
    (await http.get<TaskList>(taskPath(boardId), { params: filters, signal }))
      .data,
  get: async (boardId: string, id: string, signal?: AbortSignal) =>
    (await http.get<TaskDetail>(taskPath(boardId, id), { signal })).data,
  create: async (boardId: string, data: TaskCreate) =>
    (await http.post<TaskDetail>(taskPath(boardId), data)).data,
  update: async (boardId: string, id: string, data: TaskUpdate) =>
    (await http.patch<TaskDetail>(taskPath(boardId, id), data)).data,
  status: async (boardId: string, id: string, status: ManualStatus) =>
    (await http.patch<Task>(`${taskPath(boardId, id)}/status`, { status }))
      .data,
  complete: async (boardId: string, id: string, comment?: string | null) =>
    (await http.post<Task>(`${taskPath(boardId, id)}/complete`, { comment }))
      .data,
  reopen: async (
    boardId: string,
    id: string,
    status: "todo" | "in_progress" = "todo",
  ) =>
    (await http.post<Task>(`${taskPath(boardId, id)}/reopen`, { status })).data,
  remove: async (boardId: string, id: string) => {
    await http.delete(taskPath(boardId, id));
  },
};
