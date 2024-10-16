import { Outlet } from "react-router-dom";
import NavBar from "../components/NavBar";
import { HStack } from "@chakra-ui/react";

const RootLayout = () => {
  return (
    <HStack gap={0} h="100vh">
      <NavBar />
      <Outlet />
    </HStack>
  );
};

export default RootLayout;
