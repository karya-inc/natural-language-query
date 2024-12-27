import { HStack } from "@chakra-ui/react";
import ErrorBoundary from "../components/ErrorBoundary";
import NavBar from "../components/NavBar";
import { ChatBot } from "../pages/Chat";
import useChatHistory from "./utils";
import useNavBar from "../components/NavBar/useNavBar";
import SavedQuery from "../components/SavedQuery";
import { SavedQueryContext } from "../components/NavBar/utils";
import Error from "../components/Error";

const RootLayout = () => {
  const {
    messages,
    setMessages,
    conversationStarted,
    setConversationStarted,
    id,
    setId,
  } = useChatHistory();

  const {
    history,
    setHistory,
    getAllHistory,
    savedQueries,
    getAllSavedQueries,
    navOpen,
    setNavOpen,
    savedQueryData,
    setSavedQueryData,
    getSavedQueryTableData,
    postQueryToGetId,
    savedQueryTableData,
    setSavedQueryTableData,
    savedId,
    setSavedQueries,
  } = useNavBar();

  return (
    <ErrorBoundary fallback={<Error />}>
      <SavedQueryContext.Provider value={{ setSavedQueries }}>
        <HStack gap={0} h="100vh" position={{ base: "relative" }}>
          {navOpen && (
            <NavBar
              setNavOpen={setNavOpen}
              history={history}
              getAllHistory={getAllHistory}
              savedQueries={savedQueries}
              getAllSavedQueries={getAllSavedQueries}
              setConversationStarted={setConversationStarted}
              setId={setId}
              setMessages={setMessages}
              setSavedQueryData={setSavedQueryData}
              setSavedQueryTableData={setSavedQueryTableData}
            />
          )}

          {savedId ? (
            <SavedQuery
              savedQueryData={savedQueryData}
              navOpen={navOpen}
              setNavOpen={setNavOpen}
              getSavedQueryTableData={getSavedQueryTableData}
              postQueryToGetId={postQueryToGetId}
              savedQueryTableData={savedQueryTableData}
              setSavedQueryTableData={setSavedQueryTableData}
            />
          ) : (
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
          )}
        </HStack>
      </SavedQueryContext.Provider>
    </ErrorBoundary>
  );
};

export default RootLayout;
