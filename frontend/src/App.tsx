import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import RootLayout from "./layouts/RootLayout";
import { CheckUserAuth } from "./components/CheckUserAuth";
import ErrorBoundary from "./components/ErrorBoundary";
import { createContext, useState, Dispatch, SetStateAction } from "react";
import { baseUrl } from "./config";

interface RouteContextType {
  sessionId: string;
  setSessionId: Dispatch<SetStateAction<string>>;
  savedQueryId: string;
  setSavedQueryId: Dispatch<SetStateAction<string>>;
}

export const RouteContext = createContext<RouteContextType>({
  sessionId: "",
  setSessionId: () => {},
  savedQueryId: "",
  setSavedQueryId: () => {},
});

function App() {
  const [sessionId, setSessionId] = useState("");
  const [savedQueryId, setSavedQueryId] = useState("");

  return (
    <ErrorBoundary
      fallback={<div>Something went wrong. Please try again later.</div>}
    >
      <RouteContext.Provider
        value={{
          sessionId,
          setSessionId,
          savedQueryId,
          setSavedQueryId,
        }}
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
      </RouteContext.Provider>
    </ErrorBoundary>
  );
}

export default App;
