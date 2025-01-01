import { useEffect } from "react";
import {
  Box,
  Flex,
  VStack,
  Text,
  HStack,
  Icon,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
} from "@chakra-ui/react";
import { GoSidebarExpand } from "react-icons/go";
import { useNavigate } from "react-router-dom";
import CFImage from "../CloudflareImage";
import { BACKEND_URL, baseUrl } from "../../config";
import { Message } from "../../pages/Chat";
import "./index.css";

type HistoryItem = {
  session_id: string;
  nlq: string;
};

type SavedQuery = {
  sql_query_id: string;
  name: string;
  description: string;
};

type NavBarProps = {
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
  history: HistoryItem[];
  getAllHistory: (url: string) => void;
  savedQueries: SavedQuery[];
  getAllSavedQueries: (url: string) => void;
  setConversationStarted: (arg: boolean) => void;
  setId: (arg: string) => void;
  setMessages: (arg: Message[]) => void;
  setSavedQueryData: (arg: {
    name: string;
    description: string;
    sql_query_id: string;
  }) => void;
  setSavedQueryTableData: (arg: Record<string, unknown>[]) => void;
};

type UserDetails = {
  name: string;
  email: string;
};

const NavBar = ({
  setNavOpen,
  history,
  getAllHistory,
  savedQueries,
  getAllSavedQueries,
  setConversationStarted,
  setId,
  setMessages,
  setSavedQueryData,
  setSavedQueryTableData,
}: NavBarProps) => {
  const navigate = useNavigate();
  const userDetails: UserDetails = localStorage.getItem("userDetails")
    ? JSON.parse(localStorage.getItem("userDetails") as string)
    : {
        name: "",

        email: "",
      };

  const { name, email } = userDetails;

  const chatHistoryStyles = {
    ":hover": {
      background: "gray.700",
      color: "gray.300",
      cursor: "pointer",
      rounded: "md",
    },
  };

  useEffect(() => {
    getAllHistory(`${BACKEND_URL}/fetch_history`);
    getAllSavedQueries(`${BACKEND_URL}/queries`);
  }, []);

  const handleHistory = (id: string) => {
    setId(id);
    navigate(`${baseUrl}/session/${id}`);
  };

  const handleSavedQuery = (query: SavedQuery) => {
    setSavedQueryTableData([]);
    setId(query.sql_query_id);
    setSavedQueryData({
      name: query.name,
      description: query.description,
      sql_query_id: query.sql_query_id,
    });
    navigate(`${baseUrl}/saved/${query.sql_query_id}`);
  };

  return (
    <VStack
      bg="#2a2d3d"
      align="center"
      position={{ base: "absolute", md: "inherit" }}
      top={{ base: 0, md: "unset" }}
      left={{ base: 0, md: "unset" }}
      h="100vh"
      w={{ base: "70%", md: "50%", xl: "25%" }}
      alignItems="flex-start"
      zIndex={10}
    >
      <HStack w="full" justify="space-between" p="6">
        <Flex
          fontSize="2xl"
          bgGradient="linear(to-br, impactGreen, #C8E56E)"
          bgClip="text"
          fontWeight="bold"
          gap={2}
          onClick={() => {
            navigate(baseUrl);
            setConversationStarted(false);
            setMessages([]);
          }}
          cursor="pointer"
        >
          <CFImage cfsrc="karya-logo" boxSize={8} />
          <Box>Kalai</Box>
        </Flex>
        <Icon
          as={GoSidebarExpand}
          stroke="gray.400"
          strokeWidth={1}
          fontSize="xl"
          cursor="pointer"
          onClick={() => setNavOpen((prev: boolean) => !prev)}
        />
      </HStack>
      <Accordion allowToggle w="full" color="gray.400" flex={1}>
        <AccordionItem border={"none"}>
          <AccordionButton>
            <AccordionIcon />
            <Box flex="1" textAlign="left" fontWeight="bold" pl={2}>
              Chat History
            </Box>
          </AccordionButton>
          <AccordionPanel
            display="flex"
            flexDirection="column"
            maxH="70vh"
            overflow="auto"
          >
            {history.length > 0 ? (
              history.map((chat, index) => (
                <Text
                  pl={2}
                  key={`${chat.session_id}-${index}`}
                  py={3}
                  sx={chatHistoryStyles}
                  onClick={() => handleHistory(chat.session_id)}
                >
                  {chat.nlq}
                </Text>
              ))
            ) : (
              <Text fontSize="sm" pl={2}>
                No chat history available.
              </Text>
            )}
          </AccordionPanel>
        </AccordionItem>

        <AccordionItem border={"none"}>
          <AccordionButton>
            <AccordionIcon />
            <Box flex="1" textAlign="left" fontWeight="bold" pl={2}>
              Saved Queries
            </Box>
          </AccordionButton>
          <AccordionPanel
            display="flex"
            flexDirection="column"
            maxH="70vh"
            overflow="auto"
          >
            {savedQueries.length > 0 ? (
              savedQueries.map((query, index) => (
                <Text
                  pl={2}
                  key={`${query.sql_query_id}-${index}`}
                  py={3}
                  sx={chatHistoryStyles}
                  onClick={() => handleSavedQuery(query)}
                >
                  {query.name}
                </Text>
              ))
            ) : (
              <Text fontSize="sm" pl={2}>
                No saved queries yet.
              </Text>
            )}
          </AccordionPanel>
        </AccordionItem>
      </Accordion>
      <VStack
        color="gray.400"
        align="flex-start"
        fontWeight="normal"
        gap={{ base: 2, xl: 0 }}
        p={6}
      >
        <Text>{name || "Dan Abrahmov"}</Text>
        <Text>{email || "danabrahmov@gmail.com"}</Text>
      </VStack>
    </VStack>
  );
};

export default NavBar;
