import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import ErrorBoundary from "./components/ErrorBoundary";

function App() {
  return (
    <ErrorBoundary
      fallback={<div>Something went wrong. Please try again later.</div>}
    >
      <RouterProvider router={router} />
    </ErrorBoundary>
  );
}

export default App;
