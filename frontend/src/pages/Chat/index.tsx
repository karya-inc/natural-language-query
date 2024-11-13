import React, { useState, useEffect, useCallback, useRef, memo } from "react";
import useChat from "./useChat";
import {
  VStack,
  HStack,
  Box,
  InputGroup,
  Input,
  InputRightElement,
  IconButton,
  Text,
  Icon,
  SkeletonCircle,
} from "@chakra-ui/react";
import { GoSidebarCollapse } from "react-icons/go";
import { HiArrowUp } from "react-icons/hi";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import BotGreeting from "./BotGreeting";
import CFImage from "../../components/CloudflareImage";

export type Message = {
  id: string;
  message: string;
  role: "user" | "bot";
  timestamp: number;
  components?: MessageComponent[];
  newMessage?: boolean;
  session_id?: string;
};

export type MessageComponent = {
  type: "button" | "spec";
  label: string;
  content: { [key: string]: string | number | boolean | object };
};

export type ChatBotProps = {
  pastMessages?: Message[];
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
};

export type NLQUpdateEvent = (
  | {
    kind: "UPDATE";
    status: string;
  }
  | {
    kind: "RESPONSE";
    type: "TEXT";
    payload: string;
  }
  | {
    kind: "RESPONSE";
    type: "TABLE";
    payload: Record<string, string>[];
  }
) & {
  session_id: string;
};

export function ChatBot({
  pastMessages = [],
  navOpen,
  setNavOpen,
}: ChatBotProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(pastMessages);
  const [isFetching, setIsFetching] = useState(false);
  const [error, setError] = useState("");
  const [conversationStarted, setConversationStarted] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { postChat } = useChat({ input, sessionId });

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setInput(e.target.value);
    },
    [],
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!input.trim()) return;

      const newMessage: Message = {
        id: Date.now().toString(),
        message: input,
        role: "user",
        timestamp: Date.now(),
        session_id: sessionId,
      };

      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInput("");
      setError("");
      setIsFetching(true);
      setConversationStarted(true);

      try {
        let collectedPayload = "";
        let updatedSessionId = sessionId;

        const reader = await postChat(import.meta.env.VITE_ENDPOINT);

        const decoder = new TextDecoder();
        let done = false;

        while (!done) {
          if (!reader) throw new Error("Reader is undefined");
          const { value, done: readerDone } = await reader.read();
          done = readerDone;

          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            try {
              const parsedChunk = JSON.parse(chunk) as NLQUpdateEvent;
              updatedSessionId = parsedChunk.session_id;
              collectedPayload += parsedChunk.response.payload;
            } catch {
              console.error("Failed to parse JSON");
            }
          }
        }

        const botMessage: Message = {
          id: Date.now().toString(),
          message: collectedPayload,
          role: "bot",
          timestamp: Date.now(),
          session_id: updatedSessionId,
        };

        setMessages((prevMessages) => [...prevMessages, botMessage]);
        setSessionId(updatedSessionId);
      } catch (error) {
        console.error("Failed to fetch response", error);
        setError("Failed to fetch response");
      } finally {
        setIsFetching(false);
      }
    },
    [input, sessionId],
  );

  return (
    <VStack
      bg="gray.900"
      align="center"
      justify="center"
      gap={8}
      w="100%"
      h="100%"
    >
      {!navOpen && (
        <Icon
          as={GoSidebarCollapse}
          stroke="gray.400"
          strokeWidth={1}
          fontSize="xl"
          cursor="pointer"
          onClick={() => setNavOpen(!navOpen)}
          position="absolute"
          top={5}
          left={5}
        />
      )}
      {!conversationStarted && <BotGreeting />}
      {conversationStarted && (
        <VStack
          w="full"
          flex={1}
          overflowY="auto"
          px={{ base: "10vw", lg: "10vw", xl: "20vw" }}
          py={12}
          gap={10}
        >
          {messages.map((msg) => (
            <MemoizedMessage key={msg.id} msg={msg} />
          ))}
          {isFetching && <FetchingSkeleton />}
          {error && <ErrorMessage error={error} />}
          <div ref={messagesEndRef} />
        </VStack>
      )}

      <VStack
        pb={6}
        bg="gray.900"
        w={{ base: "80vw", md: "60vw", xl: "40vw" }}
        alignItems="center"
        gap={2}
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
              _hover={{ borderColor: "gray.600" }}
              color="gray.400"
              _focus={{ boxShadow: "none", borderColor: "gray.600" }}
              value={input}
              onChange={handleInputChange}
              isDisabled={isFetching}
            />
            <InputRightElement width="3rem">
              <IconButton
                type="submit"
                icon={<Icon as={HiArrowUp} stroke="gray.900" strokeWidth={1} />}
                aria-label="Send"
                bg="impactGreen"
                size="sm"
                _hover={{ bg: "#338F67" }}
              />
            </InputRightElement>
          </InputGroup>
        </form>
        <Text color="gray.500" fontSize="sm">
          Kalai can make mistakes. Check important info.
        </Text>
      </VStack>
    </VStack>
  );
}

// Memoized Message Component
const MemoizedMessage = memo(({ msg }: { msg: Message }) => {
  const { message, role } = msg;

  return (
    <HStack
      color="gray.50"
      w="full"
      justify={role === "user" ? "flex-end" : "flex-start"}
      align={role === "user" ? "flex-end" : "flex-start"}
      gap={{ base: 4, lg: 6, xl: 8 }}
    >
      {role === "bot" && (
        <CFImage
          cfsrc="karya-logo"
          boxSize={10}
          border="1px solid"
          borderColor="gray.600"
          borderRadius="full"
          fit="contain"
          p={2}
        />
      )}
      <VStack
        w="auto"
        align="flex-start"
        bg={role === "user" ? "#2a2d3d" : ""}
        color="gray.400"
        borderRadius="xl"
      >
        {role === "bot" ? (
          <Box className="markdown-body" pt={2}>
            <Markdown children={message} remarkPlugins={[remarkGfm]} />
          </Box>
        ) : (
          <Text p={3}>{message}</Text>
        )}
      </VStack>
    </HStack>
  );
});

// Skeleton Loader Component
const FetchingSkeleton = () => (
  <HStack w="full" gap={4}>
    <CFImage
      cfsrc="karya-logo"
      boxSize={10}
      border="1px solid"
      borderColor="gray.600"
      borderRadius={50}
      p={2}
    />
    <SkeletonCircle size="4" />
  </HStack>
);

// Error Message Component
const ErrorMessage = ({ error }: { error: string }) => (
  <HStack w="full" gap={4}>
    <CFImage
      cfsrc="karya-logo"
      boxSize={10}
      border="1px solid"
      borderColor="gray.600"
      borderRadius={50}
      p={2}
    />
    <Text color="red.400">{error ?? "Something Went Wrong"}</Text>
  </HStack>
);
