import { createBrowserRouter } from "react-router-dom";
import { ChatBot } from "../screens/Chat";
import RootLayout from "../layouts/RootLayout";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        path: "",
        element: <ChatBot />,
      },
    ],
  },
]);
