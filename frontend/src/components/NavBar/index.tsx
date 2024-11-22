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
import { redirect } from "react-router-dom";
import CFImage from "../CloudflareImage";
import useHistory from "./useChatHistory";
// import { useEffect } from "react";

const NavBar = ({
  navOpen,
  setNavOpen,
  handleHistoryClick,
}: {
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
  handleHistoryClick: (arg1: string, arg2: string) => void;
}) => {
  const {
    history,
    // getHistory
  } = useHistory();

  const chatHistoryStyles = {
    ":hover": {
      background: "gray.700",
      color: "gray.300",
      cursor: "pointer",
      rounded: "md",
    },
  };

  // useEffect(() => {
  //   getHistory(import.meta.env.VITE_CHAT_HISTORY_SESSIONS_ENDPOINT);
  // }, []);

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
          onClick={() => redirect("/")}
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
        allowMultiple
        allowToggle
        w="full"
        color="gray.400"
        flex={1}
      >
        <AccordionItem border={"none"}>
          <h2>
            <AccordionButton>
              <Box flex="1" textAlign="left" fontWeight="bold" pl={2}>
                Chat History
              </Box>
              <AccordionIcon />
            </AccordionButton>
          </h2>
          <AccordionPanel display="flex" flexDirection="column">
            {history && history.length > 0 ? (
              history.map((chat) => (
                <Text
                  pl={2}
                  key={chat.session_id}
                  py={3}
                  sx={chatHistoryStyles}
                  onClick={() =>
                    handleHistoryClick(chat.session_id, chat.user_query)
                  }
                >
                  {chat.user_query}
                </Text>
              ))
            ) : (
              <Text fontSize="sm">No chat history available.</Text>
            )}
          </AccordionPanel>
        </AccordionItem>

        <AccordionItem border={"none"}>
          <h2>
            <AccordionButton>
              <Box flex="1" textAlign="left" fontWeight="bold" pl={2}>
                Saved Queries
              </Box>
              <AccordionIcon />
            </AccordionButton>
          </h2>
          <AccordionPanel>
            <Text fontSize="sm" pl={2}>
              No saved queries yet.
            </Text>
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
