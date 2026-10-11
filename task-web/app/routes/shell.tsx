import {
  ActionIcon,
  Button,
  Group,
  Text,
  useMantineColorScheme,
} from "@mantine/core";
import { useQuery } from "@tanstack/react-query";
import { Moon, Sun } from "lucide-react";
import { NavLink, Navigate, Outlet, useLocation } from "react-router";
import { meQuery } from "../api/queries";
import { useSession } from "../shared/session";
import { Brand, ErrorState, LoadingState } from "../shared/ui";
export default function Shell() {
  const token = useSession((state) => state.token);
  const clear = useSession((state) => state.clear);
  const location = useLocation();
  const me = useQuery({ ...meQuery(), enabled: !!token });
  const { colorScheme, toggleColorScheme } = useMantineColorScheme();
  if (!token)
    return (
      <Navigate
        to="/login"
        replace
        state={{ from: location.pathname + location.search }}
      />
    );
  return (
    <>
      <header className="app-header">
        <div className="header-inner">
          <Brand />
          <nav className="main-nav" aria-label="Основная навигация">
            <NavLink to="/" end className="nav-link">
              Наши доски
            </NavLink>
            <NavLink to="/profile" className="nav-link">
              Мой профиль
            </NavLink>
          </nav>
          <Group gap="xs">
            <Text size="sm">{me.data?.name}</Text>
            <ActionIcon
              variant="subtle"
              onClick={toggleColorScheme}
              aria-label={
                colorScheme === "dark" ? "Светлая тема" : "Тёмная тема"
              }
            >
              {colorScheme === "dark" ? <Sun size={19} /> : <Moon size={19} />}
            </ActionIcon>
            <Button variant="subtle" size="xs" onClick={clear}>
              Выйти
            </Button>
          </Group>
        </div>
      </header>
      <main className="app-main">
        {me.isPending ? (
          <LoadingState />
        ) : me.isError ? (
          <ErrorState error={me.error} retry={() => void me.refetch()} />
        ) : (
          <Outlet />
        )}
      </main>
    </>
  );
}
