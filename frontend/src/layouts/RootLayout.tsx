import { HStack } from "@chakra-ui/react";
import ErrorBoundary from "../components/ErrorBoundary";
import NavBar from "../components/NavBar";
import { ChatBot } from "../pages/Chat";
import { useState } from "react";
import useChatHistory from "./utils";
import useNavBar from "../components/NavBar/useNavBar";

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);

  const {
    messages,
    setMessages,
    conversationStarted,
    setConversationStarted,
    id,
    setId,
  } = useChatHistory();
  const { history, setHistory, getHistory, savedQueries, getSavedQueries } =
    useNavBar();

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
            history={history}
            getHistory={getHistory}
            savedQueries={savedQueries}
            getSavedQueries={getSavedQueries}
            setConversationStarted={setConversationStarted}
            setId={setId}
            setMessages={setMessages}
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
          id={id ?? ""}
          setId={setId}
        />
      </HStack>
    </ErrorBoundary>
  );
};

export default RootLayout;
