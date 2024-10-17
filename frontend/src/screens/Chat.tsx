import {
  Avatar,
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Icon,
  IconButton,
  Image,
  Input,
  InputGroup,
  InputRightElement,
  Skeleton,
  Text,
  VStack,
} from "@chakra-ui/react";
import React, { useEffect, useRef, useState, useCallback } from "react";
import {
  HiArrowUp,
  HiCheck,
  HiOutlineClipboard,
  HiUser,
} from "react-icons/hi2";
import Markdown from "react-markdown";
import { useTypewriter } from "react-simple-typewriter";
import remarkGfm from "remark-gfm";
import "../styles/markdown.css";
import "github-markdown-css";

const BOT_NAME = "Kalai";

export type Message = {
  id: string; // uuid string
  message: string;
  role: "user" | "bot";
  timestamp: number; // epoch timestamp Date.now()
  components?: MessageComponent[];
  newMessage?: boolean;
};

export type MessageComponent = {
  type: "button" | "spec";
  label: string;
  content: {
    [key: string]: any;
  };
};

export type ChatBotProps = {
  pastMessages?: Message[];
};

export function ChatBot({ pastMessages = [] }: ChatBotProps) {
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>(pastMessages);
  const [isFetching, setIsFetching] = useState<boolean>(false);
  const [error, setError] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    console.log(messages);
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      // handle form submission
    },
    []
  );

  return (
    <Container
      bg="gray.900"
      centerContent
      alignItems="center"
      justifyContent="center"
      maxW="100vw"
      h="100%"
    >
      <Flex gap={2}>
        <Image src="karya-logo.svg" w="40px" h="40px" alt="Karya logo" />
        <Heading color="gray.500" fontWeight="normal">
          Hello, how can{" "}
          <Box
            as="span"
            fontWeight="extrabold"
            bgGradient="linear(to-br, impactGreen, #C8E56E)"
            bgClip="text"
          >
            {BOT_NAME}
          </Box>{" "}
          help you today?
        </Heading>
      </Flex>
      <VStack w="full" pb={12}>
        {messages.map((msg) => (
          <Message key={msg.id} msg={msg} scrollToBottom={scrollToBottom} />
        ))}
        {isFetching && (
          <Box my={1} color="gray.50" w="full" gap={4} display="flex">
            <Avatar size="sm" bg={"gray.700"} src={"/og-image.jpg"} />
            <Box w="full" pt={1}>
              <Heading size="sm" mb={1.5}>
                {BOT_NAME}
              </Heading>
              <VStack
                align="start"
                spacing={1.5}
                flexDirection={"column"}
                w="full"
              >
                {[0, 1, 2].map((num) => (
                  <Skeleton key={num} height="15px" />
                ))}
              </VStack>
            </Box>
          </Box>
        )}
        {error && (
          <Box
            my={1}
            color="gray.50"
            w="full"
            gap={4}
            display="flex"
            role="group"
          >
            <Avatar size="sm" bg={"gray.700"} src={"/og-image.jpg"} />
            <Box w="full" pt={1}>
              <Heading size="sm" mb={1.5}>
                {BOT_NAME}
              </Heading>
              <Text color="red.400">{error}</Text>
              <Button
                size="xs"
                w="min"
                variant="ghost"
                color="gray.500"
                border="solid 1.5px"
                borderColor="gray.500"
                _hover={{
                  bg: "gray.800",
                }}
                opacity={0}
                _groupHover={{ opacity: 1 }}
              >
                Retry
              </Button>
            </Box>
          </Box>
        )}
        <div ref={messagesEndRef} />
      </VStack>
      <VStack
        pb={6}
        w="full"
        bg="gray.900"
        maxW="4xl"
        display="flex"
        flexDirection="column"
        alignItems="center"
        gap={2}
        zIndex={10}
      >
        <form onSubmit={handleSubmit} style={{ flex: 1, width: "100%" }}>
          <InputGroup size="lg">
            <Input
              placeholder="Type your message here"
              size="lg"
              bg="gray.900"
              rounded="xl"
              boxShadow="sm"
              border="solid 1px"
              borderColor="gray.700"
              pr="3rem"
              _hover={{
                borderColor: "gray.600",
              }}
              color="gray.50"
              _focus={{
                boxShadow: "none",
                borderColor: "gray.600",
              }}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              isDisabled={isFetching}
            />
            <InputRightElement width="3rem">
              <IconButton
                type="submit"
                icon={
                  <Icon as={HiArrowUp} stroke={"gray.900"} strokeWidth={1} />
                }
                aria-label="Send"
                bg="impactGreen"
                size="sm"
                _hover={{ bg: "#338F67" }}
              />
            </InputRightElement>
          </InputGroup>
        </form>
        <Text color="gray.500" fontSize="sm">
          &copy; Copyright Karya 2024 — Present
        </Text>
      </VStack>
    </Container>
  );
}

const Message = React.memo(
  ({ msg, scrollToBottom }: { msg: Message; scrollToBottom: () => void }) => {
    const { message, role, newMessage } = msg;
    const [copyLabel, setCopyLabel] = useState<string>("Copy");
    const [copyIcon, setCopyIcon] = useState<React.ReactElement>(
      <Icon as={HiOutlineClipboard} />
    );
    const [text] = useTypewriter({
      words: [message],
      loop: 1,
      typeSpeed: 20,
      onType: useCallback(
        (count: number) => {
          if (count % 10 === 0) scrollToBottom();
        },
        [scrollToBottom]
      ),
      onLoopDone: useCallback(() => {
        scrollToBottom();
      }, [scrollToBottom]),
    });

    const handleCopy = useCallback(() => {
      navigator.clipboard.writeText(message);
      setCopyIcon(<Icon as={HiCheck} />);
      setCopyLabel("Copied");
      setTimeout(() => {
        setCopyLabel("Copy");
        setCopyIcon(<Icon as={HiOutlineClipboard} />);
      }, 1000);
    }, [message]);

    return (
      <Box my={2} color="gray.50" display="flex" w="full" gap={4}>
        <Avatar
          size="sm"
          bg={role === "bot" ? "gray.700" : "impactGreen"}
          icon={
            role === "user" ? (
              <Icon as={HiUser} boxSize={5} color="gray.900" />
            ) : undefined
          }
          src={role === "bot" ? "/og-image.jpg" : undefined}
        />
        <Box
          display="flex"
          flexDirection="column"
          w="full"
          pt={1}
          gap={1.5}
          role="group"
          position="relative"
        >
          <Heading size="sm">{role === "user" ? "You" : BOT_NAME}</Heading>
          {role === "bot" ? (
            <Box className="markdown-body">
              <Markdown
                children={newMessage ? text : message}
                remarkPlugins={[remarkGfm]}
              />
            </Box>
          ) : (
            <Text>{message}</Text>
          )}
          <Button
            size="xs"
            w="min"
            variant="ghost"
            color="gray.500"
            border="solid 1.5px"
            borderColor="gray.500"
            _hover={{
              bg: "gray.800",
            }}
            opacity={0}
            leftIcon={copyIcon}
            _groupHover={{ opacity: 1 }}
            onClick={handleCopy}
          >
            {copyLabel}
          </Button>
        </Box>
      </Box>
    );
  }
);
