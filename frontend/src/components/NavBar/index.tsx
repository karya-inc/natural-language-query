import {
  Avatar,
  Box,
  Flex,
  Image,
  VStack,
  Text,
  HStack,
  Heading,
} from "@chakra-ui/react";
import chatHistory from "../../data/history.json";
import "./index.css";
import { redirect } from "react-router-dom";
import CFImage from "../CloudflareImage";

const NavBar = () => {
  const chatHistoryStyles = {
    ":hover": {
      color: "gray.400",
      cursor: "pointer",
    },
  };
  return (
    <VStack
      p="6"
      pr={0}
      bg="#2a2d3d"
      align="center"
      h="100vh"
      w="20%"
      alignItems="flex-start"
      gap={12}
    >
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
          {chatHistory &&
            chatHistory.map((chat) => {
              return (
                <Text key={chat.id} fontSize="lg" sx={chatHistoryStyles}>
                  {chat.message}
                </Text>
              );
            })}
        </VStack>
      </VStack>
      <HStack color="gray.500" fontWeight="normal" gap={4}>
        <Avatar name="Dan Abrahmov" src="https://bit.ly/dan-abramov" />
        <VStack align="start" gap={0}>
          <Text>Dan Abrahmov</Text>
          <Text>danabrahmov@gmail.com</Text>
        </VStack>
      </HStack>
    </VStack>
  );
};

export default NavBar;
