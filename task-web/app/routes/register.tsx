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
import { Link, Navigate, useNavigate } from "react-router";
import { z } from "zod";
import { authApi } from "../api/resources";
import { errorMessage } from "../api/client";
import { useSession } from "../shared/session";
import { AuthLayout } from "../shared/ui";
const schema = z.object({
  name: z.string().trim().min(1, "Введите имя"),
  email: z.email("Введите корректную почту"),
  phone: z
    .string()
    .regex(
      /^\+[1-9]\d{7,14}$/,
      "Введите телефон с кодом страны, например +79991234567",
    ),
  password: z.string().min(1, "Введите пароль"),
  birthday: z.string(),
  timezone: z
    .string()
    .min(1, "Укажите часовой пояс")
    .refine((value) => {
      try {
        new Intl.DateTimeFormat("ru", { timeZone: value });
        return true;
      } catch {
        return false;
      }
    }, "Укажите корректный часовой пояс"),
});
export default function Register() {
  const token = useSession((state) => state.token);
  const navigate = useNavigate();
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      password: "",
      birthday: "",
      timezone:
        Intl.DateTimeFormat().resolvedOptions().timeZone || "Europe/Moscow",
    },
  });
  const register = useMutation({
    mutationFn: (data: z.infer<typeof schema>) =>
      authApi.register({
        ...data,
        birthday: data.birthday ? `${data.birthday}T00:00:00` : null,
      }),
    onSuccess: () => void navigate("/login?registered=1", { replace: true }),
  });
  if (token) return <Navigate to="/" replace />;
  const field = (name: keyof z.infer<typeof schema>) => ({
    ...form.register(name),
    error: form.formState.errors[name]?.message,
  });
  return (
    <AuthLayout>
      <Stack gap="lg">
        <div>
          <Title order={2}>Начнём с знакомства</Title>
          <Text c="dimmed">Создайте своё пространство для семейных дел.</Text>
        </div>
        <form onSubmit={form.handleSubmit((data) => register.mutate(data))}>
          <Stack>
            <TextInput
              label="Ваше имя"
              autoComplete="name"
              {...field("name")}
            />
            <TextInput
              label="Электронная почта"
              type="email"
              autoComplete="email"
              {...field("email")}
            />
            <TextInput
              label="Телефон"
              type="tel"
              placeholder="+79991234567"
              autoComplete="tel"
              {...field("phone")}
            />
            <PasswordInput
              label="Пароль"
              visibilityToggleButtonProps={{
                "aria-label": "Показать или скрыть пароль",
              }}
              autoComplete="new-password"
              {...field("password")}
            />
            <TextInput
              label="Дата рождения"
              type="date"
              description="Необязательно"
              {...field("birthday")}
            />
            <TextInput label="Часовой пояс" {...field("timezone")} />
            {register.isError && (
              <Alert color="red">{errorMessage(register.error)}</Alert>
            )}
            <Button type="submit" loading={register.isPending}>
              Создать аккаунт
            </Button>
          </Stack>
        </form>
        <Text size="sm">
          Уже есть аккаунт?{" "}
          <Anchor component={Link} to="/login">
            Войти
          </Anchor>
        </Text>
      </Stack>
    </AuthLayout>
  );
}
