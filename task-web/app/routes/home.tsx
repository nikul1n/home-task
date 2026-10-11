import {
  Badge,
  Button,
  Card,
  Group,
  Modal,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { useQuery } from "@tanstack/react-query";
import { ArrowUpRight, LayoutGrid, Plus } from "lucide-react";
import { Link } from "react-router";
import { boardsQuery, meQuery, useCreateBoard } from "../api/queries";
import { BoardForm } from "../features/forms";
import {
  EmptyState,
  ErrorState,
  LoadingState,
  PageHeading,
} from "../shared/ui";
export default function Home() {
  const boards = useQuery(boardsQuery());
  const me = useQuery(meQuery());
  const create = useCreateBoard();
  const [opened, { open, close }] = useDisclosure();
  return (
    <>
      <section className="hero">
        <Badge variant="light" mb="md">
          Место для самого важного
        </Badge>
        <Title order={1} mb="sm">
          Хорошо, когда мы рядом{me.data?.name ? `, ${me.data.name}` : ""}.
        </Title>
        <Text c="dimmed" maw={620}>
          Планируйте домашние дела, помогайте друг другу и оставляйте больше
          времени для того, что любите.
        </Text>
      </section>
      <PageHeading
        title="Наши доски"
        description="Каждому общему плану — своё уютное место."
        action={
          <Button leftSection={<Plus size={18} />} onClick={open}>
            Создать доску
          </Button>
        }
      />
      {boards.isPending ? (
        <LoadingState />
      ) : boards.isError ? (
        <ErrorState error={boards.error} retry={() => void boards.refetch()} />
      ) : boards.data.length === 0 ? (
        <EmptyState title="Начните с первой доски">
          Например, «Домашние дела», «Покупки» или «Выходные вместе».
        </EmptyState>
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }}>
          {boards.data.map((board) => (
            <Link
              key={board.id}
              to={`/boards/${board.id}`}
              className="board-link"
            >
              <Card className="board-card">
                <Stack gap="md">
                  <Group justify="space-between">
                    <LayoutGrid color="var(--mantine-color-sage-6)" />
                    <ArrowUpRight size={18} />
                  </Group>
                  <Title order={3}>{board.title}</Title>
                  <Text c="dimmed" size="sm" lineClamp={3}>
                    {board.description ||
                      "Общие планы и маленькие шаги к большому уюту."}
                  </Text>
                </Stack>
              </Card>
            </Link>
          ))}
        </SimpleGrid>
      )}
      <Modal opened={opened} onClose={close} title="Новая семейная доска">
        <BoardForm
          pending={create.isPending}
          onSubmit={(data) => create.mutate(data, { onSuccess: close })}
        />
      </Modal>
    </>
  );
}
