import { createBrowserRouter, Navigate } from "react-router-dom";
import { ChatBot } from "../screens/Chat";
import RootLayout from "../layouts/RootLayout";
import { CheckUserAuth } from "../components/CheckUserAuth";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <Navigate to={import.meta.env.BASE_URL} />,
  },
  {
    path: import.meta.env.BASE_URL,
    element: <CheckUserAuth forComponent={<RootLayout />} />,
    children: [
      {
        index: true,
        element: <ChatBot />,
      },
    ],
  },
]);
