import { memo, useCallback, useEffect, useRef } from "react";
import { HStack, VStack, Text, Button, Icon } from "@chakra-ui/react";
import ChatActions from "./ChatActions";
import CFImage from "./CloudflareImage";
import ChatTable from "../components/ChatTable";
import { Message } from "../pages/Chat";
import { BACKEND_URL } from "../config";
import { IoCloudDownloadOutline } from "react-icons/io5";
import { handleDownload, messageActionStyles } from "../pages/Chat/utils";

type RowData = {
  id: string;
  content: string;
  timestamp: Date;
};

const MemoizedMessage = memo(
  ({
    msg,
    handleExecute,
  }: {
    msg: Message;
    handleExecute: (arg1: string, arg2: string) => void;
  }) => {
    const { message, role, type, execution_id } = msg;
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = useCallback(() => {
      messagesEndRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "nearest",
      });
    }, []);

    useEffect(() => {
      scrollToBottom();
    }, [msg]);

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
          gap={4}
        >
          {role === "bot" ? (
            type === "execution" ? (
              <VStack gap={0} align="flex-start">
                <Text py={2} color={"gray.400"}>
                  Please click to execute the query
                </Text>
                <Button
                  color="gray.400"
                  bg="gray.700"
                  _hover={{ bg: "gray.600", color: "gray.400" }}
                  onClick={() =>
                    handleExecute(
                      `${BACKEND_URL}/execution_result/${execution_id}`,
                      execution_id
                    )
                  }
                >
                  Execute
                </Button>
              </VStack>
            ) : (type === "error" || type === "text") &&
              typeof message === "string" ? (
              <Text py={2} color={type === "error" ? "red.400" : "gray.400"}>
                {message}
              </Text>
            ) : (
              typeof message === "object" && (
                <ChatTable data={message as RowData[]} />
              )
            )
          ) : (
            typeof message === "string" && <Text p={3}>{message}</Text>
          )}
          {type !== "execution" && type !== "error" ? (
            <ChatActions msg={msg} />
          ) : (
            <HStack
              sx={messageActionStyles}
              w={7}
              h={7}
              align="center"
              justify="center"
              cursor="pointer"
            >
              <Icon
                as={IoCloudDownloadOutline}
                stroke="gray.200"
                strokeWidth={2}
                fontSize="md"
                onClick={() => {
                  if (Array.isArray(message)) {
                    handleDownload(message as Record<string, string>[]);
                  }
                }}
              />
            </HStack>
          )}
        </VStack>
        {<div ref={messagesEndRef} />}
      </HStack>
    );
  }
);
export default MemoizedMessage;
