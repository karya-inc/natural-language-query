import { createBrowserRouter } from "react-router-dom";
import { ChatBot } from "../screens/Chat";
import RootLayout from "../layouts/RootLayout";
import { CheckUserAuth } from "../components/CheckUserAuth";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        path: "",
        element: <CheckUserAuth forComponent={<ChatBot />} />,
      },
    ],
  },
]);
