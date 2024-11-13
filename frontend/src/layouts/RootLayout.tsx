import NavBar from "../components/NavBar";
import { HStack } from "@chakra-ui/react";
import { useState } from "react";
import { ChatBot, Message } from "../pages/Chat";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);

  function getData(session_id: string, user_query: string) {
    return [
      {
        id: 1,
        message: user_query,
        role: "user",
        timestamp: Date.now(),
        session_id: session_id,
      },
      {
        id: 2,
        message: "What would you like to search?",
        role: "bot",
        timestamp: Date.now(),
        session_id: session_id,
      },
      {
        id: 3,
        message: "I would like to search for...",
        role: "user",
        timestamp: Date.now(),
        session_id: session_id,
      },
      {
        id: 1,
        message: "Please be specific",
        role: "bot",
        timestamp: Date.now(),
        session_id: session_id,
      },
    ];
  }

  function handleHistoryClick(session_id: string, user_query: string) {
    const data = getData(session_id, user_query);
    setMessages((prevMessages) => {
      return [...prevMessages, ...data];
    });
  }

  return (
    <HStack gap={0} h="100vh" position={{ base: "relative" }}>
      {navOpen && (
        <NavBar
          navOpen={navOpen}
          setNavOpen={setNavOpen}
          handleHistoryClick={handleHistoryClick}
        />
      )}
      <ChatBot
        messages={messages}
        setMessages={setMessages}
        navOpen={navOpen}
        setNavOpen={setNavOpen}
      />
    </HStack>
  );
};

export default RootLayout;
