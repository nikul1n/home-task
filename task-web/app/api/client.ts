import axios from "axios";
import { useSession } from "../shared/session";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 15_000,
  headers: { "Content-Type": "application/json" },
});

http.interceptors.request.use((config) => {
  const token = useSession.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});
http.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      !error.config?.url?.startsWith("/auth/")
    ) {
      // Ignore late responses belonging to a previous session.
      const token = useSession.getState().token;
      if (token && error.config?.headers.Authorization === `Bearer ${token}`)
        useSession.getState().clear();
    }
    return Promise.reject(error);
  },
);

export function errorMessage(error: unknown): string {
  if (!axios.isAxiosError(error))
    return "Не удалось выполнить действие. Попробуйте ещё раз.";
  if (!error.response)
    return "Не удалось связаться с сервером. Проверьте подключение.";
  const messages: Record<number, string> = {
    400: "Не удалось выполнить запрос. Проверьте введённые данные.",
    401:
      error.config?.url === "/auth/login"
        ? "Неверная почта или пароль."
        : "Сессия истекла. Войдите снова.",
    403: "У вас нет прав на это действие.",
    404: "Запись не найдена или больше недоступна.",
    409: "Такая запись уже существует или была изменена.",
    422: "Проверьте заполнение полей: сервер отклонил данные.",
    429: "Слишком много запросов. Попробуйте немного позже.",
  };
  return (
    messages[error.response.status] ||
    "На сервере произошла ошибка. Попробуйте позже."
  );
}
