import {
  Alert,
  Anchor,
  Button,
  Card,
  Select,
  Stack,
  TextInput,
} from "@mantine/core";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Link, useParams } from "react-router";
import { notifications } from "@mantine/notifications";
import { useBoardActions } from "../api/queries";
import { PageHeading } from "../shared/ui";
const schema = z.object({
  user_id: z.uuid("Введите корректный идентификатор"),
  role: z.enum(["admin", "member", "viewer"]),
});
export default function MembersPage() {
  const { boardId = "" } = useParams();
  const { addMember } = useBoardActions(boardId);
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { user_id: "", role: "member" },
  });
  return (
    <>
      <Anchor component={Link} to={`/boards/${boardId}`} size="sm">
        ← К доске
      </Anchor>
      <div style={{ marginTop: 20 }}>
        <PageHeading
          title="Ближе к общим планам"
          description="Добавьте близкого человека к делам этой доски."
        />
      </div>
      <Card maw={600}>
        <Stack>
          <Alert color="sage">
            Попросите близкого скопировать свой идентификатор в профиле.
            Добавлять участников могут пользователи с соответствующими правами.
          </Alert>
          <form
            onSubmit={form.handleSubmit((data) =>
              addMember.mutate(data, {
                onSuccess: () => {
                  form.reset();
                  notifications.show({
                    title: "Вы теперь вместе",
                    message: "Участник добавлен на доску.",
                    color: "sage",
                  });
                },
              }),
            )}
          >
            <Stack>
              <TextInput
                label="Идентификатор пользователя"
                {...form.register("user_id")}
                error={form.formState.errors.user_id?.message}
              />
              <Controller
                name="role"
                control={form.control}
                render={({ field }) => (
                  <Select
                    label="Роль"
                    data={[
                      { value: "admin", label: "Администратор" },
                      { value: "member", label: "Участник" },
                      { value: "viewer", label: "Наблюдатель" },
                    ]}
                    value={field.value}
                    onChange={(value) => field.onChange(value || "member")}
                  />
                )}
              />
              <Button type="submit" loading={addMember.isPending}>
                Добавить участника
              </Button>
            </Stack>
          </form>
        </Stack>
      </Card>
    </>
  );
}
