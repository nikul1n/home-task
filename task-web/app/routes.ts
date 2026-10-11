import {
  type RouteConfig,
  index,
  layout,
  route,
} from "@react-router/dev/routes";
export default [
  route("login", "routes/login.tsx"),
  route("register", "routes/register.tsx"),
  layout("routes/shell.tsx", [
    index("routes/home.tsx"),
    route("boards/:boardId", "routes/board.tsx"),
    route("boards/:boardId/tasks/:taskId", "routes/task.tsx"),
    route("boards/:boardId/members", "routes/members.tsx"),
    route("profile", "routes/profile.tsx"),
  ]),
  route("*", "routes/not-found.tsx"),
] satisfies RouteConfig;
