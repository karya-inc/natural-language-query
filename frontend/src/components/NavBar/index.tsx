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
import "./index.css";
import { useNavigate } from "react-router-dom";
import CFImage from "../CloudflareImage";
import { useEffect } from "react";
import { BACKEND_URL, baseUrl } from "../../config";
import { Message } from "../../pages/Chat";

const NavBar = ({
  navOpen,
  setNavOpen,
  history,
  getHistory,
  savedQueries,
  getSavedQueries,
  setConversationStarted,
  setId,
  setMessages,
}: {
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
  history: { session_id: string; nlq: string }[];
  getHistory: (arg: string) => void;
  savedQueries: { session_id: string; nlq: string }[];
  getSavedQueries: (arg: string) => void;
  setConversationStarted: (arg: boolean) => void;
  setId: (arg: string) => void;
  setMessages: (arg: Message[]) => void;
}) => {
  const navigate = useNavigate();
  const chatHistoryStyles = {
    ":hover": {
      background: "gray.700",
      color: "gray.300",
      cursor: "pointer",
      rounded: "md",
    },
  };

  useEffect(() => {
    getHistory(`${BACKEND_URL}/fetch_history`);
    getSavedQueries(`${BACKEND_URL}/queries`);
  }, []);

  function handleClick(session_id: string) {
    setId(session_id);
    navigate(`${baseUrl}/session/${session_id}`);
  }

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
          onClick={() => setNavOpen(!navOpen)}
        />
      </HStack>
      <Accordion
        defaultIndex={[0]}
        allowToggle
        w="full"
        color="gray.400"
        flex={1}
      >
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
              history.map((chat: { session_id: string; nlq: string }) => (
                <Text
                  pl={2}
                  key={chat.session_id}
                  py={3}
                  sx={chatHistoryStyles}
                  onClick={() => handleClick(chat.session_id)}
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
            h="70vh"
            overflow="auto"
          >
            {savedQueries && savedQueries.length > 0 ? (
              savedQueries.map((chat: { session_id: string; nlq: string }) => (
                <Text
                  pl={2}
                  key={chat.session_id}
                  py={3}
                  sx={chatHistoryStyles}
                  onClick={() => handleClick(chat.session_id)}
                >
                  {chat.nlq}
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
        <Text>Dan Abrahmov</Text>
        <Text>danabrahmov@gmail.com</Text>
      </VStack>
    </VStack>
  );
};

export default NavBar;
