import { Button, Stack, Text, Title } from "@mantine/core";
import { Link } from "react-router";
export default function NotFound() {
  return (
    <main className="boot-screen">
      <Stack align="center">
        <Title>Кажется, мы свернули не туда</Title>
        <Text c="dimmed">Такой страницы нет. Вернёмся к нашим планам?</Text>
        <Button component={Link} to="/">
          На главную
        </Button>
      </Stack>
    </main>
  );
}
