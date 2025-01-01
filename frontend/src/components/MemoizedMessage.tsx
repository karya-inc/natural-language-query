import { memo } from "react";
import { HStack, VStack, Text, Button } from "@chakra-ui/react";
import ChatActions from "./ChatActions";
import CFImage from "./CloudflareImage";
import ChatTable from "../components/ChatTable";
import { Message } from "../pages/Chat";
import { BACKEND_URL } from "../config";
import { ArrowUpDown } from "lucide-react";
import { Column } from "@tanstack/react-table";

type RowData = {
  id: string;
  content: string;
  timestamp: Date;
};

type ColProps = {
  header: ({ column }: { column: Column<RowData> }) => JSX.Element;
  accessorKey: string;
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

    let colDefs: ColProps[] = [];
    if (message !== null) {
      colDefs = Object.keys(message[0]).map((key) => ({
        header: ({ column }) => {
          return (
            <Button
              variant="plain"
              size={"md"}
              onClick={() =>
                column.toggleSorting(column.getIsSorted() === "asc")
              }
            >
              {key}
              <ArrowUpDown className="ml-2 h-4 w-4" />
            </Button>
          );
        },
        accessorKey: key,
      }));
    }

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
                <ChatTable columns={colDefs} data={message as RowData[]} />
              )
            )
          ) : (
            typeof message === "string" && <Text p={3}>{message}</Text>
          )}
          {type !== "execution" && <ChatActions msg={msg} />}
        </VStack>
      </HStack>
    );
  }
);

export default MemoizedMessage;
