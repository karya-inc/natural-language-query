import { HStack, Icon, Tooltip } from "@chakra-ui/react";
import { FaRegSave } from "react-icons/fa";
import { IoInformationCircleOutline } from "react-icons/io5";
import { LuDownloadCloud } from "react-icons/lu";
import { downloadObjectAs } from "./utils";
import { Message } from ".";

const ChatActions = ({ msg }: { msg: Message }) => {
  const { message, role, type, kind, query } = msg;

  const handleDownload = (report: Record<string, string>[]) => {
    const today = new Date();
    const date = today.getDate();
    const month = today.getMonth() + 1;
    const year = today.getFullYear();

    downloadObjectAs(report, `Table-${year}-${month}-${date}.csv`, "csv");
  };

  const messageActionStyles = {
    ":hover": {
      backgroundColor: "gray.700",
      rounded: "lg",
    },
  };
  return (
    role === "bot" &&
    kind !== "UPDATE" && (
      <HStack gap={1}>
        {type === "table" && (
          <HStack
            sx={messageActionStyles}
            w={7}
            h={7}
            align="center"
            justify="center"
            cursor="pointer"
          >
            <Icon
              as={LuDownloadCloud}
              stroke="gray.200"
              strokeWidth={2}
              fontSize="md"
              onClick={() => handleDownload(JSON.parse(message))}
            />
          </HStack>
        )}
        <HStack
          sx={messageActionStyles}
          w={7}
          h={7}
          align="center"
          cursor="pointer"
          justify="center"
        >
          <Icon
            as={FaRegSave}
            stroke="gray.200"
            strokeWidth={4}
            fontSize="md"
          />
        </HStack>
        <Tooltip
          label={query || "No query available"}
          hasArrow
          bg="gray.700"
          color="gray.400"
          py={1}
          px={2}
          borderRadius="md"
        >
          <HStack
            sx={messageActionStyles}
            w={7}
            h={7}
            align="center"
            justify="center"
          >
            <Icon
              as={IoInformationCircleOutline}
              stroke="gray.200"
              strokeWidth={4}
              fontSize="md"
            />
          </HStack>
        </Tooltip>
      </HStack>
    )
  );
};

export default ChatActions;
