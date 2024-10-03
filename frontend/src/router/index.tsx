import { createBrowserRouter } from "react-router-dom";
import { ChatBot } from "../screens/Chat";

export const router = createBrowserRouter([
  { path: "/", element: <ChatBot /> },
]);
