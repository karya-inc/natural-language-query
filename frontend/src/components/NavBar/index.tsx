import {
  Box,
  Flex,
  VStack,
  Text,
  HStack,
  Heading,
  Icon,
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
      color: "gray.400",
      cursor: "pointer",
    },
  };

  // useEffect(() => {
  //   getHistory(import.meta.env.VITE_CHAT_HISTORY_SESSIONS_ENDPOINT);
  // }, []);

  return (
    <VStack
      p="6"
      pr={0}
      bg="#2a2d3d"
      align="center"
      position={{ base: "absolute", md: "inherit" }}
      top={{ base: 0, md: "unset" }}
      left={{ base: 0, md: "unset" }}
      h="100vh"
      w={{ base: "70%", md: "50%", xl: "25%" }}
      alignItems="flex-start"
      gap={12}
      zIndex={10}
    >
      <HStack w="full" justify="space-between" pr={4}>
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
      <VStack
        align="start"
        gap={4}
        flex={1}
        color="gray.500"
        w="full"
        fontWeight="normal"
        overflow="auto"
      >
        <Heading fontSize="sm" color="gray.400">
          Chat History
        </Heading>
        <VStack
          gap={4}
          align="flex-start"
          w="full"
          h="full"
          overflow="auto"
          pr={4}
        >
          {history &&
            history.map((chat) => {
              return (
                <Text
                  key={chat.session_id}
                  fontSize="lg"
                  sx={chatHistoryStyles}
                  onClick={() =>
                    handleHistoryClick(chat.session_id, chat.user_query)
                  }
                >
                  {chat.user_query}
                </Text>
              );
            })}
        </VStack>
      </VStack>
      <VStack
        color="gray.500"
        align="flex-start"
        fontWeight="normal"
        gap={{ base: 2, xl: 0 }}
      >
        <Text>Dan Abrahmov</Text>
        <Text>danabrahmov@gmail.com</Text>
      </VStack>
    </VStack>
  );
};

export default NavBar;
