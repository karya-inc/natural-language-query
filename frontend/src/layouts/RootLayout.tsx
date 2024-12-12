import NavBar from "../components/NavBar";
import { HStack } from "@chakra-ui/react";
import { useState } from "react";
import { ChatBot } from "../pages/Chat";
import useChatHistory from "./utils";
import { BACKEND_URL } from "../config";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  const [conversationStarted, setConversationStarted] = useState(false);
  const { messages, setMessages, getChatHistory } = useChatHistory();

  function handleHistoryClick(session_id: string) {
    setConversationStarted(true);
    getChatHistory(`${BACKEND_URL}/fetch_session_history/${session_id}`);
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
