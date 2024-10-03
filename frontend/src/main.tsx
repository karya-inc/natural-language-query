import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import {
  ChakraBaseProvider,
  defineStyle,
  defineStyleConfig,
  extendTheme,
} from "@chakra-ui/react";
import DefaultTheme from "./themes/default/Index";

const buttonVariants = Object.fromEntries(
  Object.entries(DefaultTheme.buttonTheme).map(([name, props]) => [
    name,
    defineStyle(props),
  ]),
);
const theme = extendTheme({
  colors: DefaultTheme.colors,
  components: { Button: defineStyleConfig({ variants: buttonVariants }) },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ChakraBaseProvider theme={theme}>
      <App />
    </ChakraBaseProvider>
  </StrictMode>,
);
