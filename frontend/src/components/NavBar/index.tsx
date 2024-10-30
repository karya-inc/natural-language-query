import {
  Avatar,
  Box,
  Flex,
  Image,
  VStack,
  Text,
  HStack,
  Heading,
  Icon,
} from "@chakra-ui/react";
import chatHistory from "../../data/history.json";
import { GoSidebarExpand } from "react-icons/go";
import "./index.css";
import { redirect } from "react-router-dom";

const NavBar = ({
  navOpen,
  setNavOpen,
}: {
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
}) => {
  const chatHistoryStyles = {
    ":hover": {
      color: "gray.400",
      cursor: "pointer",
    },
  };

  console.log(navOpen);

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
      w={{ base: "70%", md: "50%", xl: "20%" }}
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
          <Image src="../../../public/karya-logo.svg" boxSize={8} />
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
      <HStack color="gray.500" fontWeight="normal" gap={{ base: 2, xl: 4 }}>
        <Avatar name="Dan Abrahmov" src="https://bit.ly/dan-abramov" />
        <VStack align="start" gap={0}>
          <Text>Dan Abrahmov</Text>
        </VStack>
      </HStack>
    </VStack>
  );
};

export default NavBar;
