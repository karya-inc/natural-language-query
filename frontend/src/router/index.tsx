import { createBrowserRouter, Navigate } from "react-router-dom";
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
  },
]);
