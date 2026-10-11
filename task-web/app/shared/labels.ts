import { format, isValid, parseISO } from "date-fns";
import { ru } from "date-fns/locale";
export const statusLabels = {
  todo: "Нужно сделать",
  in_progress: "В процессе",
  done: "Готово",
  cancelled: "Отменено",
};
export const importanceLabels = {
  low: "Без спешки",
  medium: "Обычная",
  high: "Важная",
  critical: "Срочная",
};
export const statusOptions = Object.entries(statusLabels).map(
  ([value, label]) => ({ value, label }),
);
export const importanceOptions = Object.entries(importanceLabels).map(
  ([value, label]) => ({ value, label }),
);
export function displayDate(value: string | null | undefined) {
  if (!value) return "Не указана";
  const date = parseISO(value);
  return isValid(date)
    ? format(date, "d MMMM yyyy, HH:mm", { locale: ru })
    : "Не указана";
}
