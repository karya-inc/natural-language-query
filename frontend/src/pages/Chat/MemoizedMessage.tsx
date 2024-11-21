import { memo } from "react";
import { Message } from ".";
import { HStack, VStack, Text } from "@chakra-ui/react";
import CFImage from "../../components/CloudflareImage";
import ChatTable from "../../components/ChatTable";
import ChatActions from "./ChatActions";

const MemoizedMessage = memo(({ msg }: { msg: Message }) => {
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
          type === "text" || type === "error" ? (
            <Text py={2} color={type === "error" ? "red.400" : "gray.400"}>
              {message}
            </Text>
          ) : (
            <ChatTable data={message} />
          )
        ) : (
          <Text p={3}>{message}</Text>
        )}
        <ChatActions msg={msg} />
      </VStack>
    </HStack>
  );
});

export default MemoizedMessage;
