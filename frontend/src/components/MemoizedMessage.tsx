import { memo } from "react";
import { HStack, VStack, Text, Button } from "@chakra-ui/react";
import ChatActions from "./ChatActions";
import CFImage from "./CloudflareImage";
import ChatTable from "./ChatTable";
import { Message } from "../pages/Chat";

const MemoizedMessage = memo(
  ({
    msg,
    getTableData,
  }: {
    msg: Message;
    getTableData: (arg: string) => void;
  }) => {
    const { message, role, type } = msg;

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
                  onClick={() => getTableData(message)}
                >
                  Execute
                </Button>
              </VStack>
            ) : type === "text" || type === "error" ? (
              <Text py={2} color={type === "error" ? "red.400" : "gray.400"}>
                {message}
              </Text>
            ) : (
              <ChatTable data={message} />
            )
          ) : (
            <Text p={3}>{message}</Text>
          )}
          {type !== "execution" && <ChatActions msg={msg} />}
        </VStack>
      </HStack>
    );
  }
);

export default MemoizedMessage;
