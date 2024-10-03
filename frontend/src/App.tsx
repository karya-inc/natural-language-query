import { Container } from "@chakra-ui/react";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";

function App() {
  return (
    <Container bg="gray.900" maxW="full" minH="100%">
      <RouterProvider router={router} />
    </Container>
  );
}

export default App;
