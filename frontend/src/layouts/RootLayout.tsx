import { HStack } from "@chakra-ui/react";
import ErrorBoundary from "../components/ErrorBoundary";
import NavBar from "../components/NavBar";
import { ChatBot } from "../pages/Chat";
import { useState } from "react";
import useChatHistory from "./utils";
import { BACKEND_URL } from "../config";
import useNavBar from "../components/NavBar/useNavBar";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  const [conversationStarted, setConversationStarted] = useState(false);
  const { messages, setMessages, getChatHistory } = useChatHistory();
  const { history, setHistory, getHistory, savedQueries, getSavedQueries } =
    useNavBar();

  function handleHistoryClick(session_id: string) {
    setConversationStarted(true);
    getChatHistory(`${BACKEND_URL}/fetch_session_history/${session_id}`);
  }

  return (
    <ErrorBoundary
      fallback={
        <div>Something went wrong in the layout. Please refresh the page.</div>
      }
    >
      <HStack gap={0} h="100vh" position={{ base: "relative" }}>
        {navOpen && (
          <NavBar
            navOpen={navOpen}
            setNavOpen={setNavOpen}
            handleHistoryClick={handleHistoryClick}
            history={history}
            getHistory={getHistory}
            savedQueries={savedQueries}
            getSavedQueries={getSavedQueries}
          />
        )}
        <ChatBot
          messages={messages}
          setMessages={setMessages}
          setHistory={setHistory}
          navOpen={navOpen}
          setNavOpen={setNavOpen}
          conversationStarted={conversationStarted}
          setConversationStarted={setConversationStarted}
        />
      </HStack>
    </ErrorBoundary>
  );
};

export default RootLayout;
