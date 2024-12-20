import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import { CheckUserAuth } from "./components/CheckUserAuth";
import ErrorBoundary from "./components/ErrorBoundary";
import { baseUrl } from "./config";

function App() {
  return (
    <ErrorBoundary
      fallback={<div>Something went wrong. Please try again later.</div>}
    >
      <Router>
        <Routes>
          <Route path="/" element={<Navigate to={baseUrl} />} />
          <Route
            path={baseUrl}
            element={<CheckUserAuth forComponent={<RootLayout />} />}
          />
          <Route
            path={`${baseUrl}/session/:sessionHistoryId`}
            element={<CheckUserAuth forComponent={<RootLayout />} />}
          />
          <Route
            path={`${baseUrl}/saved/:savedId`}
            element={<CheckUserAuth forComponent={<RootLayout />} />}
          />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
