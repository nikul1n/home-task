import { Button, Select, Stack, Textarea, TextInput } from "@mantine/core";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { format, parseISO } from "date-fns";
import type { BoardCreate, TaskCreate } from "../api/contracts";
import { importanceOptions } from "../shared/labels";

const title = z
  .string()
  .trim()
  .min(1, "Введите название")
  .max(255, "Не более 255 символов");
const boardSchema = z.object({ title, description: z.string() });
export function BoardForm({
  initial,
  pending,
  onSubmit,
}: {
  initial?: BoardCreate;
  pending: boolean;
  onSubmit: (data: BoardCreate) => void;
}) {
  const form = useForm<z.infer<typeof boardSchema>>({
    resolver: zodResolver(boardSchema),
    defaultValues: {
      title: initial?.title || "",
      description: initial?.description || "",
    },
  });
  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <Stack>
        <TextInput
          label="Название доски"
          autoFocus
          maxLength={255}
          {...form.register("title")}
          error={form.formState.errors.title?.message}
        />
        <Textarea
          label="Описание"
          autosize
          minRows={3}
          {...form.register("description")}
        />
        <Button type="submit" loading={pending}>
          Сохранить доску
        </Button>
      </Stack>
    </form>
  );
}
const taskSchema = z.object({
  title,
  description: z.string(),
  importance: z.enum(["low", "medium", "high", "critical"]),
  deadline: z
    .string()
    .refine(
      (value) => !value || !Number.isNaN(new Date(value).getTime()),
      "Укажите корректную дату",
    ),
  responsible_id: z.union([
    z.literal(""),
    z.uuid("Введите корректный идентификатор"),
  ]),
});
export function TaskForm({
  initial,
  pending,
  onSubmit,
}: {
  initial?: TaskCreate;
  pending: boolean;
  onSubmit: (data: TaskCreate) => void;
}) {
  const form = useForm<z.infer<typeof taskSchema>>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: initial?.title || "",
      description: initial?.description || "",
      importance: initial?.importance || "medium",
      deadline: initial?.deadline
        ? format(parseISO(initial.deadline), "yyyy-MM-dd'T'HH:mm")
        : "",
      responsible_id: initial?.responsible_id || "",
    },
  });
  return (
    <form
      onSubmit={form.handleSubmit((data) =>
        onSubmit({
          ...data,
          description: data.description || null,
          deadline: data.deadline
            ? new Date(data.deadline).toISOString()
            : null,
          responsible_id: data.responsible_id || null,
        }),
      )}
    >
      <Stack>
        <TextInput
          label="Что нужно сделать?"
          autoFocus
          maxLength={255}
          {...form.register("title")}
          error={form.formState.errors.title?.message}
        />
        <Textarea
          label="Подробности"
          autosize
          minRows={3}
          {...form.register("description")}
        />
        <Controller
          control={form.control}
          name="importance"
          render={({ field }) => (
            <Select
              label="Важность"
              data={importanceOptions}
              value={field.value}
              onChange={(value) => field.onChange(value || "medium")}
              error={form.formState.errors.importance?.message}
            />
          )}
        />
        <TextInput
          label="Срок"
          type="datetime-local"
          description="Время на вашем устройстве"
          {...form.register("deadline")}
          error={form.formState.errors.deadline?.message}
        />
        <TextInput
          label="Идентификатор исполнителя"
          description="Необязательно. Можно указать свой идентификатор из профиля."
          {...form.register("responsible_id")}
          error={form.formState.errors.responsible_id?.message}
        />
        <Button type="submit" loading={pending}>
          Сохранить задачу
        </Button>
      </Stack>
    </form>
  );
}
