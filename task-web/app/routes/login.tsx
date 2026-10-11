import {
  Alert,
  Anchor,
  Button,
  PasswordInput,
  Stack,
  Text,
  TextInput,
  Title,
} from "@mantine/core";
import { useMutation } from "@tanstack/react-query";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Link,
  Navigate,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router";
import { z } from "zod";
import { authApi } from "../api/resources";
import { errorMessage } from "../api/client";
import { useSession } from "../shared/session";
import { AuthLayout } from "../shared/ui";
const schema = z.object({
  email: z.email("Введите корректную почту"),
  password: z.string().min(1, "Введите пароль"),
});
export default function Login() {
  const session = useSession();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const from: unknown = location.state?.from;
  const target =
    typeof from === "string" &&
    from.startsWith("/") &&
    !from.startsWith("//") &&
    !from.includes("\\") &&
    !/^\/(login|register)(?:[/?#]|$)/.test(from)
      ? from
      : "/";
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });
  const login = useMutation({
    mutationFn: authApi.login,
    onSuccess: (data) => {
      session.setToken(data.access_token);
      void navigate(target, { replace: true });
    },
  });
  if (session.token) return <Navigate to={target} replace />;
  return (
    <AuthLayout>
      <Stack gap="lg">
        <div>
          <Title order={2}>С возвращением</Title>
          <Text c="dimmed">Ваши близкие и общие планы уже рядом.</Text>
        </div>
        {params.has("registered") && (
          <Alert color="sage">Аккаунт создан. Теперь можно войти.</Alert>
        )}
        <form onSubmit={form.handleSubmit((data) => login.mutate(data))}>
          <Stack>
            <TextInput
              label="Электронная почта"
              type="email"
              autoComplete="email"
              {...form.register("email")}
              error={form.formState.errors.email?.message}
            />
            <PasswordInput
              label="Пароль"
              visibilityToggleButtonProps={{
                "aria-label": "Показать или скрыть пароль",
              }}
              autoComplete="current-password"
              {...form.register("password")}
              error={form.formState.errors.password?.message}
            />
            {login.isError && (
              <Alert color="red">{errorMessage(login.error)}</Alert>
            )}
            <Button type="submit" fullWidth loading={login.isPending}>
              Войти
            </Button>
          </Stack>
        </form>
        <Text size="sm">
          Ещё нет аккаунта?{" "}
          <Anchor component={Link} to="/register">
            Создать аккаунт
          </Anchor>
        </Text>
      </Stack>
    </AuthLayout>
  );
}
