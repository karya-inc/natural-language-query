import React, { useState, useEffect, useCallback, useRef } from "react";
import useChat from "./useChat";
import {
  VStack,
  HStack,
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
import BotGreeting from "../../components/BotGreeting";
import CFImage from "../../components/CloudflareImage";
import { BACKEND_URL } from "../../config";
import MemoizedMessage from "../../components/MemoizedMessage";

export type Message = {
  id: number;
  message: string | Record<string, unknown>[];
  role: "user" | "bot";
  timestamp: number;
  kind?: "UPDATE" | "TEXT" | "TABLE";
  type?: "text" | "table" | "error" | "execution";
  query?: string;
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
  messages: Message[];
  setMessages: (
    arg: Message[] | ((prevMessages: Message[]) => Message[])
  ) => void;
  setHistory: (
    arg:
      | { session_id: string; nlq: string }[]
      | ((
          prevHistory: { session_id: string; nlq: string }[]
        ) => { session_id: string; nlq: string }[])
  ) => void;
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
  conversationStarted: boolean;
  setConversationStarted: (arg: boolean) => void;
};

export type NLQUpdateEvent = (
  | {
      kind: "UPDATE";
      status: string;
    }
  | {
      kind: "RESPONSE";
      type: "TEXT" | "ERROR";
      payload: string;
    }
  | {
      kind: "RESPONSE";
      type: "TABLE";
      payload: Record<string, string>[];
      query: string;
    }
) & {
  session_id: string;
};

export function ChatBot({
  messages = [],
  setMessages,
  setHistory,
  navOpen,
  setNavOpen,
  conversationStarted,
  setConversationStarted,
}: ChatBotProps) {
  const [input, setInput] = useState("");
  const [isFetching, setIsFetching] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const focusRef = useRef<HTMLInputElement>(null);
  const { postChat, getTableData } = useChat({ input, sessionId });

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    focusRef.current?.focus();
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setInput(e.target.value);
    },
    []
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      if (!input.trim()) return;

      const newMessage: Message = {
        id: Math.random(),
        message: input,
        type: "text",
        role: "user",
        timestamp: Date.now(),
      };

      setMessages((prevMessages) => [...prevMessages, newMessage]);
      setInput("");
      setIsFetching(true);
      setConversationStarted(true);

      const botMessage: Message = {
        id: Math.random(),
        message: "",
        role: "bot",
        timestamp: Date.now(),
      };

      try {
        let updatedSessionId = sessionId;

        const reader = await postChat(`${BACKEND_URL}/chat`);

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
              if (parsedChunk.kind === "UPDATE") {
                botMessage.message = parsedChunk.status;
                botMessage.type = "text";
                botMessage.kind = "UPDATE";
              } else if (parsedChunk.kind === "RESPONSE") {
                if (parsedChunk.type === "TEXT") {
                  botMessage.message = parsedChunk.payload;
                  botMessage.type = "text";
                  botMessage.kind = "TEXT";
                } else if (parsedChunk.type === "TABLE") {
                  botMessage.message = parsedChunk.payload;
                  botMessage.query = parsedChunk.query;
                  botMessage.type = "table";
                  botMessage.kind = "TABLE";
                } else if (parsedChunk.type === "ERROR") {
                  botMessage.message = parsedChunk.payload;
                  botMessage.type = "error";
                }
              }
              setMessages((prevMessages) => {
                if (prevMessages[prevMessages.length - 1].role === "bot") {
                  const updatedMessages = [...prevMessages];
                  updatedMessages[updatedMessages.length - 1] = {
                    ...botMessage,
                  };
                  return [...updatedMessages];
                }
                return [...prevMessages, botMessage];
              });
              setIsFetching(false);
            } catch (error) {
              console.error("Failed to parse JSON chunk", error);
              setIsFetching(false);
            }
          }
        }
        setHistory((prevHistory) => [
          { session_id: updatedSessionId, nlq: input },
          ...prevHistory,
        ]);

        setSessionId(updatedSessionId);
      } catch (error) {
        console.error("Failed to fetch response", error);
        botMessage.message = "Failed to fetch response";
        botMessage.type = "error";
        setMessages((prevMessages) => {
          if (prevMessages[prevMessages.length - 1].role === "bot") {
            const updatedMessages = [...prevMessages];
            updatedMessages[updatedMessages.length - 1] = {
              ...botMessage,
            };
            return [...updatedMessages];
          }
          return [...prevMessages, botMessage];
        });
      }
    },
    [input, sessionId]
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
          px={{ base: "10vw", xl: "20vw" }}
          py={12}
          gap={10}
        >
          {messages.map((msg) => (
            <MemoizedMessage
              key={msg.id}
              msg={msg}
              getTableData={getTableData}
            />
          ))}
          {isFetching && <FetchingSkeleton />}
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
              placeholder="Please type the message here"
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
              ref={focusRef}
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
