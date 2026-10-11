import { useEffect, useState } from "react";
import {
  Anchor,
  Badge,
  Button,
  Group,
  Modal,
  Pagination,
  Select,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useDebouncedValue, useDisclosure } from "@mantine/hooks";
import { useQuery } from "@tanstack/react-query";
import { Check, Plus, Search, Settings, Users } from "lucide-react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router";
import clsx from "clsx";
import {
  boardQuery,
  meQuery,
  tasksQuery,
  useBoardActions,
  useTaskActions,
} from "../api/queries";
import type { Importance, TaskStatus } from "../api/contracts";
import { BoardForm, TaskForm } from "../features/forms";
import {
  displayDate,
  importanceLabels,
  importanceOptions,
  statusLabels,
  statusOptions,
} from "../shared/labels";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeading,
} from "../shared/ui";

export default function BoardPage() {
  const { boardId = "" } = useParams();
  const navigate = useNavigate();
  const [params, setParams] = useSearchParams();
  const [search, setSearch] = useState(params.get("search") || "");
  const [debounced] = useDebouncedValue(search.trim(), 300);
  useEffect(() => {
    setSearch(params.get("search") || "");
  }, [params.get("search")]);
  useEffect(() => {
    if (debounced === (params.get("search") || "")) return;
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        if (debounced) next.set("search", debounced);
        else next.delete("search");
        next.delete("page");
        return next;
      },
      { replace: true },
    );
  }, [debounced, setParams]);
  const statusValue = params.get("status") || "";
  const importanceValue = params.get("importance") || "";
  const status = statusOptions.some((item) => item.value === statusValue)
    ? (statusValue as TaskStatus)
    : undefined;
  const importance = importanceOptions.some(
    (item) => item.value === importanceValue,
  )
    ? (importanceValue as Importance)
    : undefined;
  const requestedPage = Number(params.get("page") || 1);
  const page =
    Number.isSafeInteger(requestedPage) && requestedPage > 0
      ? requestedPage
      : 1;
  const limit = 20;
  const board = useQuery(boardQuery(boardId));
  const me = useQuery(meQuery());
  const querySearch = params.get("search")?.trim();
  const tasks = useQuery(
    tasksQuery(boardId, {
      status,
      importance,
      search:
        querySearch && querySearch.length >= 2 && querySearch.length <= 100
          ? querySearch
          : undefined,
      limit,
      offset: (page - 1) * limit,
    }),
  );
  const actions = useTaskActions(boardId);
  const boardActions = useBoardActions(boardId);
  const [createOpened, createModal] = useDisclosure();
  const [editOpened, editModal] = useDisclosure();
  const [deleteOpened, deleteModal] = useDisclosure();
  const setFilter = (key: string, value: string | null) =>
    setParams((current) => {
      const next = new URLSearchParams(current);
      if (value) next.set(key, value);
      else next.delete(key);
      if (key !== "page") next.delete("page");
      return next;
    });
  if (board.isPending) return <LoadingState />;
  if (board.isError)
    return (
      <ErrorState error={board.error} retry={() => void board.refetch()} />
    );
  const owner = board.data.creator_id === me.data?.id;
  const busy = actions.complete.isPending || actions.reopen.isPending;
  return (
    <>
      <Anchor component={Link} to="/" size="sm">
        ← Все доски
      </Anchor>
      <div style={{ marginTop: 20 }}>
        <PageHeading
          title={board.data.title}
          description={board.data.description || "Заботимся о доме вместе."}
          action={
            <Group>
              <Button
                variant="light"
                component={Link}
                to={`/boards/${boardId}/members`}
                leftSection={<Users size={16} />}
              >
                Участники
              </Button>
              {owner && (
                <Button
                  variant="subtle"
                  aria-label="Настройки доски"
                  onClick={editModal.open}
                >
                  <Settings size={18} />
                </Button>
              )}
              <Button
                onClick={createModal.open}
                leftSection={<Plus size={18} />}
              >
                Добавить дело
              </Button>
            </Group>
          }
        />
      </div>
      <Group mb="lg" align="flex-start">
        <TextInput
          aria-label="Поиск задач"
          placeholder="Найти дело…"
          leftSection={<Search size={16} />}
          value={search}
          onChange={(event) => setSearch(event.currentTarget.value)}
          maxLength={100}
          error={
            search.trim().length === 1 ? "Введите минимум 2 символа" : undefined
          }
          style={{ flex: 1, minWidth: 200 }}
        />
        <Select
          aria-label="Статус"
          placeholder="Все статусы"
          data={statusOptions}
          value={status || null}
          clearable
          onChange={(value) => setFilter("status", value)}
        />
        <Select
          aria-label="Важность"
          placeholder="Любая важность"
          data={importanceOptions}
          value={importance || null}
          clearable
          onChange={(value) => setFilter("importance", value)}
        />
      </Group>
      {tasks.isPending ? (
        <LoadingState />
      ) : tasks.isError ? (
        <ErrorState error={tasks.error} retry={() => void tasks.refetch()} />
      ) : (
        <section
          aria-busy={tasks.isFetching}
          style={{ opacity: tasks.isPlaceholderData ? 0.6 : 1 }}
        >
          {tasks.data.items.length === 0 ? (
            <EmptyState title="Здесь пока нет дел">
              Добавьте задачу или измените фильтры.
            </EmptyState>
          ) : (
            tasks.data.items.map((task) => (
              <article
                key={task.id}
                className={clsx("task-row", { done: task.status === "done" })}
              >
                <div className="task-content">
                  <Anchor
                    component={Link}
                    to={`/boards/${boardId}/tasks/${task.id}`}
                    className="task-title"
                    fw={600}
                  >
                    {task.title}
                  </Anchor>
                  <Group gap="xs" mt={6}>
                    <Badge
                      variant="light"
                      color={task.status === "done" ? "sage" : "gray"}
                    >
                      {statusLabels[task.status]}
                    </Badge>
                    <Text size="xs" c="dimmed">
                      {importanceLabels[task.importance]}
                    </Text>
                    {task.deadline && (
                      <Text size="xs" c="dimmed">
                        До {displayDate(task.deadline)}
                      </Text>
                    )}
                  </Group>
                </div>
                <Button
                  variant="light"
                  size="xs"
                  disabled={busy || tasks.isPlaceholderData}
                  leftSection={
                    task.status === "done" ? undefined : <Check size={14} />
                  }
                  onClick={() =>
                    task.status === "done" || task.status === "cancelled"
                      ? actions.reopen.mutate(task.id)
                      : actions.complete.mutate(task.id)
                  }
                >
                  {task.status === "done" || task.status === "cancelled"
                    ? "Вернуть"
                    : "Готово"}
                </Button>
              </article>
            ))
          )}
          {tasks.data.total != null ? (
            <Pagination
              mt="xl"
              total={Math.max(1, Math.ceil(tasks.data.total / limit))}
              value={page}
              onChange={(value) => setFilter("page", String(value))}
              disabled={tasks.isPlaceholderData}
              aria-label="Страницы задач"
            />
          ) : (
            <Group mt="xl">
              <Button
                disabled={page === 1 || tasks.isPlaceholderData}
                onClick={() => setFilter("page", String(page - 1))}
              >
                Назад
              </Button>
              <Button
                disabled={
                  tasks.data.items.length < limit || tasks.isPlaceholderData
                }
                onClick={() => setFilter("page", String(page + 1))}
              >
                Далее
              </Button>
            </Group>
          )}
        </section>
      )}
      <Modal
        opened={createOpened}
        onClose={createModal.close}
        title="Новое дело"
      >
        <TaskForm
          pending={actions.create.isPending}
          onSubmit={(data) =>
            actions.create.mutate(data, { onSuccess: createModal.close })
          }
        />
      </Modal>
      <Modal
        opened={editOpened}
        onClose={editModal.close}
        title="Настройки доски"
      >
        <Stack>
          <BoardForm
            initial={board.data}
            pending={boardActions.update.isPending}
            onSubmit={(data) =>
              boardActions.update.mutate(data, { onSuccess: editModal.close })
            }
          />
          <Button color="red" variant="subtle" onClick={deleteModal.open}>
            Удалить доску
          </Button>
        </Stack>
      </Modal>
      <Modal
        opened={deleteOpened}
        onClose={deleteModal.close}
        title="Удалить доску?"
      >
        <Stack>
          <Text>Доска «{board.data.title}» станет недоступна. Продолжить?</Text>
          <Button
            color="red"
            loading={boardActions.remove.isPending}
            onClick={() =>
              boardActions.remove.mutate(undefined, {
                onSuccess: () => void navigate("/"),
              })
            }
          >
            Удалить доску
          </Button>
          <Button variant="default" onClick={deleteModal.close}>
            Оставить
          </Button>
        </Stack>
      </Modal>
    </>
  );
}
