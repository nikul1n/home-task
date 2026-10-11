import { Button, Card, createTheme, Input, Modal } from "@mantine/core";

export const theme = createTheme({
  primaryColor: "sage",
  colors: {
    sage: [
      "#f1f7f2",
      "#e1eee3",
      "#c0dcc5",
      "#9acba4",
      "#7ab987",
      "#64ac74",
      "#51965f",
      "#417d4e",
      "#356440",
      "#2b5335",
    ],
  },
  fontFamily: '"Segoe UI", system-ui, sans-serif',
  headings: {
    fontFamily: '"Segoe UI", system-ui, sans-serif',
    fontWeight: "650",
  },
  defaultRadius: "md",
  components: {
    Button: Button.extend({ defaultProps: { radius: "xl" } }),
    Card: Card.extend({
      defaultProps: { radius: "lg", padding: "lg", withBorder: true },
    }),
    Input: Input.extend({ defaultProps: { size: "md" } }),
    Modal: Modal.extend({ defaultProps: { centered: true, radius: "lg" } }),
  },
});
