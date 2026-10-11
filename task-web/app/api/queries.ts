import {
  keepPreviousData,
  queryOptions,
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";
import { notifications } from "@mantine/notifications";
import { authApi, boardsApi, tasksApi } from "./resources";
import { errorMessage } from "./client";
import type {
  BoardCreate,
  BoardUpdate,
  MemberCreate,
  TaskCreate,
  TaskFilters,
  TaskUpdate,
  ManualStatus,
} from "./contracts";

export const keys = {
  me: ["me"] as const,
  boards: ["boards"] as const,
  board: (id: string) => ["boards", id] as const,
  tasks: (id: string) => ["tasks", id] as const,
  task: (boardId: string, id: string) =>
    ["tasks", boardId, "detail", id] as const,
};
export const meQuery = () =>
  queryOptions({
    queryKey: keys.me,
    queryFn: ({ signal }) => authApi.me(signal),
  });
export const boardsQuery = () =>
  queryOptions({
    queryKey: keys.boards,
    queryFn: ({ signal }) => boardsApi.list(signal),
  });
export const boardQuery = (id: string) =>
  queryOptions({
    queryKey: keys.board(id),
    queryFn: ({ signal }) => boardsApi.get(id, signal),
  });
export const tasksQuery = (id: string, filters: TaskFilters = {}) =>
  queryOptions({
    queryKey: [...keys.tasks(id), "list", filters],
    queryFn: ({ signal }) => tasksApi.list(id, filters, signal),
    placeholderData: keepPreviousData,
  });
export const taskQuery = (boardId: string, id: string) =>
  queryOptions({
    queryKey: keys.task(boardId, id),
    queryFn: ({ signal }) => tasksApi.get(boardId, id, signal),
  });

const notifyError = (error: unknown) =>
  notifications.show({
    title: "Не получилось",
    message: errorMessage(error),
    color: "red",
  });
export function useCreateBoard() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (data: BoardCreate) => boardsApi.create(data),
    onSuccess: () => client.invalidateQueries({ queryKey: keys.boards }),
    onError: notifyError,
  });
}
export function useBoardActions(id: string) {
  const client = useQueryClient();
  const invalidate = () => client.invalidateQueries({ queryKey: keys.boards });
  const update = useMutation({
    mutationFn: (data: BoardUpdate) => boardsApi.update(id, data),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const remove = useMutation({
    mutationFn: () => boardsApi.remove(id),
    onSuccess: async () => {
      client.removeQueries({ queryKey: keys.tasks(id) });
      await invalidate();
    },
    onError: notifyError,
  });
  const addMember = useMutation({
    mutationFn: (data: MemberCreate) => boardsApi.addMember(id, data),
    onSuccess: invalidate,
    onError: notifyError,
  });
  return { update, remove, addMember };
}
export function useTaskActions(boardId: string) {
  const client = useQueryClient();
  const invalidate = () =>
    client.invalidateQueries({ queryKey: keys.tasks(boardId) });
  const create = useMutation({
    mutationFn: (data: TaskCreate) => tasksApi.create(boardId, data),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const update = useMutation({
    mutationFn: ({ id, data }: { id: string; data: TaskUpdate }) =>
      tasksApi.update(boardId, id, data),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const status = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ManualStatus }) =>
      tasksApi.status(boardId, id, status),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const complete = useMutation({
    mutationFn: (id: string) => tasksApi.complete(boardId, id),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const reopen = useMutation({
    mutationFn: (id: string) => tasksApi.reopen(boardId, id),
    onSuccess: invalidate,
    onError: notifyError,
  });
  const remove = useMutation({
    mutationFn: (id: string) => tasksApi.remove(boardId, id),
    onSuccess: invalidate,
    onError: notifyError,
  });
  return { create, update, status, complete, reopen, remove };
}
