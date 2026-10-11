import {
  Avatar,
  Button,
  Card,
  CopyButton,
  Group,
  Stack,
  Text,
} from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { meQuery } from "../api/queries";
import { ErrorState, LoadingState, PageHeading } from "../shared/ui";
export default function ProfilePage() {
  const me = useQuery(meQuery());
  if (me.isPending) return <LoadingState />;
  if (me.isError)
    return <ErrorState error={me.error} retry={() => void me.refetch()} />;
  const user = me.data;
  return (
    <>
      <PageHeading
        title="Мой профиль"
        description="Чтобы близким было проще найти вас."
      />
      <Card maw={650}>
        <Stack>
          <Group>
            <Avatar
              src={user.avatar_url}
              name={user.name}
              color="sage"
              size="lg"
            />
            <div>
              <Text fw={600}>{user.name}</Text>
              <Text c="dimmed">{user.email}</Text>
            </div>
          </Group>
          <Text size="sm">Телефон: {user.phone}</Text>
          <Text size="sm">Часовой пояс: {user.timezone}</Text>
          <Text size="sm">
            Дата рождения:{" "}
            {user.birthday
              ? new Intl.DateTimeFormat("ru-RU").format(new Date(user.birthday))
              : "Не указана"}
          </Text>
          <Text size="sm" c="dimmed">
            Ваш идентификатор
          </Text>
          <Text size="sm" style={{ overflowWrap: "anywhere" }}>
            {user.id}
          </Text>
          <CopyButton value={user.id}>
            {({ copied, copy }) => (
              <Button variant="light" onClick={copy}>
                {copied ? "Скопировано" : "Скопировать идентификатор"}
              </Button>
            )}
          </CopyButton>
        </Stack>
      </Card>
    </>
  );
}
