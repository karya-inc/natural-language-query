import { HStack } from "@chakra-ui/react";
import ErrorBoundary from "../components/ErrorBoundary";
import NavBar from "../components/NavBar";
import { ChatBot } from "../pages/Chat";
import useChatHistory from "./utils";
import useNavBar from "../components/NavBar/useNavBar";
import SavedQuery from "../components/SavedQuery";
import { SavedQueryContext } from "../components/NavBar/utils";
import Error from "../components/Error";
import AddQuery from "src/components/AddQuery";

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
    getExecutionResponseById,
    executeSavedQueryByQueryId,
    savedQueryTableData,
    setSavedQueryTableData,
    savedId,
    setSavedQueries,
  } = useNavBar();

  return (
    <ErrorBoundary fallback={<Error />}>
      <SavedQueryContext.Provider value={{ setSavedQueries }}>
        <HStack
          gap={0}
          position={{ base: "relative" }}
          height="100%"
          overflow="hidden"
        >
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

          {savedId && savedQueryData.sql_query_id ? (
            <SavedQuery
              savedQueryData={savedQueryData}
              navOpen={navOpen}
              setNavOpen={setNavOpen}
              getExecutionResponseById={getExecutionResponseById}
              executeSavedQueryByQueryId={executeSavedQueryByQueryId}
              savedQueryTableData={savedQueryTableData}
              setSavedQueryTableData={setSavedQueryTableData}
            />
          ) : window.location.pathname === "/nlq/addquery" ? (
            <AddQuery navOpen={navOpen} setNavOpen={setNavOpen} />
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
