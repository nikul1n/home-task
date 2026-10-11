import {
  Anchor,
  Badge,
  Button,
  Card,
  Group,
  Modal,
  Select,
  Stack,
  Text,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate, useParams } from "react-router";
import { taskQuery, useTaskActions } from "../api/queries";
import type { ManualStatus } from "../api/contracts";
import { TaskForm } from "../features/forms";
import {
  displayDate,
  importanceLabels,
  statusLabels,
  statusOptions,
} from "../shared/labels";
import { ErrorState, LoadingState, PageHeading } from "../shared/ui";
export default function TaskPage() {
  const { boardId = "", taskId = "" } = useParams();
  const task = useQuery(taskQuery(boardId, taskId));
  const actions = useTaskActions(boardId);
  const navigate = useNavigate();
  const [editing, edit] = useDisclosure();
  const [deleting, remove] = useDisclosure();
  if (task.isPending) return <LoadingState />;
  if (task.isError)
    return <ErrorState error={task.error} retry={() => void task.refetch()} />;
  const item = task.data;
  const busy =
    actions.status.isPending ||
    actions.complete.isPending ||
    actions.reopen.isPending;
  return (
    <>
      <Anchor component={Link} to={`/boards/${boardId}`} size="sm">
        ← К доске
      </Anchor>
      <div style={{ marginTop: 20 }}>
        <PageHeading
          title={item.title}
          action={
            <Button variant="light" onClick={edit.open}>
              Редактировать
            </Button>
          }
        />
      </div>
      <Card>
        <Stack>
          <Group>
            <Badge>{statusLabels[item.status]}</Badge>
            <Text size="sm">{importanceLabels[item.importance]}</Text>
          </Group>
          <Text style={{ whiteSpace: "pre-wrap" }}>
            {item.description || "Подробности пока не добавлены."}
          </Text>
          <Text size="sm" c="dimmed">
            Автор: {item.creator.name}
          </Text>
          <Text size="sm" c="dimmed">
            Исполнитель: {item.responsible?.name || "Пока не назначен"}
          </Text>
          <Text size="sm" c="dimmed">
            Срок: {displayDate(item.deadline)}
          </Text>
          {item.completed_at && (
            <Text size="sm" c="dimmed">
              Завершено: {displayDate(item.completed_at)}
            </Text>
          )}
          <Group>
            {item.status === "done" || item.status === "cancelled" ? (
              <Button
                disabled={busy}
                onClick={() => actions.reopen.mutate(taskId)}
              >
                Вернуть в работу
              </Button>
            ) : (
              <>
                <Button
                  disabled={busy}
                  onClick={() => actions.complete.mutate(taskId)}
                >
                  Дело сделано
                </Button>
                <Select
                  aria-label="Изменить статус"
                  value={item.status}
                  data={statusOptions.filter(
                    (option) => option.value !== "done",
                  )}
                  disabled={busy}
                  onChange={(value) => {
                    if (value)
                      actions.status.mutate({
                        id: taskId,
                        status: value as ManualStatus,
                      });
                  }}
                />
              </>
            )}
            <Button variant="subtle" color="red" onClick={remove.open}>
              Удалить
            </Button>
          </Group>
        </Stack>
      </Card>
      <Modal opened={editing} onClose={edit.close} title="Редактирование дела">
        <TaskForm
          initial={item}
          pending={actions.update.isPending}
          onSubmit={(data) =>
            actions.update.mutate(
              { id: taskId, data },
              { onSuccess: edit.close },
            )
          }
        />
      </Modal>
      <Modal opened={deleting} onClose={remove.close} title="Удалить задачу?">
        <Stack>
          <Text>Задача «{item.title}» исчезнет с доски.</Text>
          <Button
            color="red"
            loading={actions.remove.isPending}
            onClick={() =>
              actions.remove.mutate(taskId, {
                onSuccess: () => void navigate(`/boards/${boardId}`),
              })
            }
          >
            Удалить
          </Button>
          <Button variant="default" onClick={remove.close}>
            Оставить
          </Button>
        </Stack>
      </Modal>
    </>
  );
}
