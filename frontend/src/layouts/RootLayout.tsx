import NavBar from "../components/NavBar";
import { HStack } from "@chakra-ui/react";
import { useState } from "react";
import { ChatBot, Message } from "../pages/Chat";
import getData from "./utils";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);

  function handleHistoryClick(session_id: string, user_query: string) {
    setConversationStarted(true);
    const data = getData(session_id, user_query);
    setMessages(data);
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
        conversationStarted={conversationStarted}
        setConversationStarted={setConversationStarted}
      />
    </HStack>
  );
};

export default RootLayout;
