import { HStack } from "@chakra-ui/react";
import ErrorBoundary from "../components/ErrorBoundary";
import NavBar from "../components/NavBar";
import { ChatBot } from "../pages/Chat";
import { createContext, useState } from "react";
import useChatHistory from "./utils";
import useNavBar from "../components/NavBar/useNavBar";
import { useParams } from "react-router-dom";
import SavedQuery from "../components/SavedQuery";

export const SavedQueryContext = createContext<{
  savedQueryDetails: {
    title: string;
    description: string;
    sql_query_id: string;
  };
  setSavedQueryDetails: React.Dispatch<
    React.SetStateAction<{
      title: string;
      description: string;
      sql_query_id: string;
    }>
  >;
}>({
  savedQueryDetails: {
    title: "",
    description: "",
    sql_query_id: "",
  },
  setSavedQueryDetails: () => {},
});

const RootLayout = () => {
  const [navOpen, setNavOpen] = useState(true);
  const [savedQueryDetails, setSavedQueryDetails] = useState({
    title: "",
    description: "",
    sql_query_id: "",
  });

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

  const { sessionHistoryId } = useParams();

  return (
    <ErrorBoundary
      fallback={
        <div>Something went wrong in the layout. Please refresh the page.</div>
      }
    >
      <SavedQueryContext.Provider
        value={{ savedQueryDetails, setSavedQueryDetails }}
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
          {sessionHistoryId ? (
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
          ) : (
            <SavedQuery />
          )}
        </HStack>
      </SavedQueryContext.Provider>
    </ErrorBoundary>
  );
};

export default RootLayout;
