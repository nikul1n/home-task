import {
  Alert,
  Button,
  Center,
  Group,
  Loader,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { AlertCircle, Heart } from "lucide-react";
import { Link } from "react-router";
import type { ReactNode } from "react";
import { errorMessage } from "../api/client";
export function Brand() {
  return (
    <Link to="/" className="brand">
      <span className="brand-icon">
        <Heart size={23} strokeWidth={1.8} />
      </span>
      рядом
      <span className="muted" style={{ fontSize: 12, fontWeight: 500 }}>
        семейные дела
      </span>
    </Link>
  );
}
export function PageHeading({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <Group justify="space-between" align="flex-start" mb="xl">
      <Stack gap={4}>
        <Title order={1} size="h2">
          {title}
        </Title>
        {description && <Text c="dimmed">{description}</Text>}
      </Stack>
      {action}
    </Group>
  );
}
export function LoadingState() {
  return (
    <Center p="xl" role="status" aria-label="Загрузка">
      <Loader color="sage" />
    </Center>
  );
}
export function ErrorState({
  error,
  retry,
}: {
  error: unknown;
  retry?: () => void;
}) {
  return (
    <Alert
      color="red"
      title="Не удалось загрузить данные"
      icon={<AlertCircle size={18} />}
    >
      <Text size="sm">{errorMessage(error)}</Text>
      {retry && (
        <Button mt="sm" variant="light" color="red" onClick={retry}>
          Повторить
        </Button>
      )}
    </Alert>
  );
}
export function EmptyState({
  title,
  children,
}: {
  title: string;
  children?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <Heart size={28} color="var(--mantine-color-sage-6)" />
      <Title order={3} mt="sm">
        {title}
      </Title>
      <Text c="dimmed" mt="xs">
        {children}
      </Text>
    </div>
  );
}
export function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <main className="auth-page">
      <aside className="auth-story">
        <Brand />
        <Title order={1} size={42}>
          Домашние дела.
          <br />
          Общие планы.
          <br />
          Больше времени вместе.
        </Title>
        <Text c="dimmed" size="lg">
          Маленькие заботы становятся легче, когда мы делим их с близкими.
        </Text>
      </aside>
      <section className="auth-form">{children}</section>
    </main>
  );
}
