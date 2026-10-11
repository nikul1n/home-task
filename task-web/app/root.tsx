import { useEffect, useState, type ReactNode } from "react";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";
import {
  ColorSchemeScript,
  MantineProvider,
  mantineHtmlProps,
} from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import axios from "axios";
import type { Route } from "./+types/root";
import { theme } from "./shared/theme";
import { useSession } from "./shared/session";
import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";
import "./app.css";

export const meta: Route.MetaFunction = () => [
  { title: "Рядом — семейные дела" },
  {
    name: "description",
    content: "Общее пространство для домашних планов и заботы друг о друге.",
  },
];
export function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru" {...mantineHtmlProps}>
      <head>
        <meta charSet="utf-8" />
        <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#f8f7f2" />
        <ColorSchemeScript defaultColorScheme="light" />
        <Meta />
        <Links />
      </head>
      <body>
        <MantineProvider theme={theme} defaultColorScheme="light">
          {children}
          <Notifications position="top-right" />
        </MantineProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
function ApiProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            retry: (count, error) =>
              count < 1 &&
              (!axios.isAxiosError(error) ||
                !error.response ||
                error.response.status >= 500),
          },
          mutations: { retry: false },
        },
      }),
  );
  useEffect(
    () => () => {
      client.clear();
    },
    [client],
  );
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
export default function App() {
  const { token, ready, hydrate } = useSession();
  useEffect(hydrate, [hydrate]);
  if (!ready) return <HydrateFallback />;
  return (
    <ApiProvider key={token || "guest"}>
      <Outlet />
    </ApiProvider>
  );
}
export function HydrateFallback() {
  return (
    <main className="boot-screen" aria-live="polite">
      Готовим уютное пространство…
    </main>
  );
}
export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  const missing = isRouteErrorResponse(error) && error.status === 404;
  return (
    <main className="boot-screen">
      <h1>{missing ? "Страница не найдена" : "Не удалось открыть страницу"}</h1>
      <p>Попробуйте вернуться на главную.</p>
      <a href="/">На главную</a>
    </main>
  );
}
