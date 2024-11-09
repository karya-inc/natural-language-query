import NavBar from "../components/NavBar";
import { HStack } from "@chakra-ui/react";
import { useState } from "react";
import { ChatBot } from "../pages/Chat";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  return (
    <HStack gap={0} h="100vh" position={{ base: "relative" }}>
      {navOpen && <NavBar navOpen={navOpen} setNavOpen={setNavOpen} />}
      <ChatBot navOpen={navOpen} setNavOpen={setNavOpen} />
    </HStack>
  );
};

export default RootLayout;
