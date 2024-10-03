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
import { useEffect, useRef, useState } from "react";
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
  const [messages, _setMessages] = useState<Message[]>(pastMessages);
  const [isFetching, _setIsFetching] = useState<boolean>(false);
  const [error, _setError] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log(messages);
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
  };

  return (
    <Container maxW="4xl" py={20} mb={20} position="relative" minH="100%">
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
      <VStack py={8} w="full" pb={12}>
        {messages.map((msg) => {
          return (
            <Message key={msg.id} msg={msg} scrollToBottom={scrollToBottom} />
          );
        })}
        {isFetching ? (
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
                  <Skeleton
                    key={num}
                    //animation={`${expandWidth} 1s infinite ease-in-out ${num * 50}ms`}
                    height="15px"
                  />
                ))}
              </VStack>
            </Box>
          </Box>
        ) : null}
        {error !== "" ? (
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
        ) : null}
        <div ref={messagesEndRef} />
      </VStack>
      <Container
        position="fixed"
        bottom={0}
        pb={10}
        pt={5}
        bg="gray.900"
        maxW="4xl"
        right={0}
        left={0}
        display="flex"
        flexDirection="column"
        alignItems="center"
        gap={1}
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
      </Container>
    </Container>
  );
}

const Message = ({
  msg,
  scrollToBottom,
}: {
  msg: Message;
  scrollToBottom: () => void;
}) => {
  const { message, role, newMessage } = msg;
  const [copyLabel, setCopyLabel] = useState<string>("Copy");
  const [copyIcon, setCopyIcon] = useState<React.ReactElement>(
    <Icon as={HiOutlineClipboard} />,
  );
  const [text] = useTypewriter({
    words: [message],
    loop: 1,
    typeSpeed: 20,
    onType(count) {
      if (count % 10 === 0) scrollToBottom();
    },
    onLoopDone() {
      scrollToBottom();
    },
  });

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
        {/* {role === 'bot' && newMessage ? <Text>{text}</Text> : <Text>{message}</Text>} */}
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
          onClick={() => {
            navigator.clipboard.writeText(message);
            setCopyIcon(<Icon as={HiCheck} />);
            setCopyLabel("Copied");
            setTimeout(() => {
              setCopyLabel("Copy");
              setCopyIcon(<Icon as={HiOutlineClipboard} />);
            }, 1000);
          }}
        >
          {copyLabel}
        </Button>
      </Box>
    </Box>
  );
};
