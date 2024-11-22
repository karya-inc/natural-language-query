import { HStack, Icon, Tooltip } from "@chakra-ui/react";
import { FaRegSave } from "react-icons/fa";
import { IoInformationCircleOutline } from "react-icons/io5";
import { LuDownloadCloud } from "react-icons/lu";
import { AiOutlineLike } from "react-icons/ai";
import { AiOutlineDislike } from "react-icons/ai";
import { downloadObjectAs } from "../pages/Chat/utils";
import { Message } from "../pages/Chat";
import { useState } from "react";

const ChatActions = ({ msg }: { msg: Message }) => {
  const { message, role, type, kind, query } = msg;
  const [liked, setLiked] = useState(false);
  const [disliked, setDisliked] = useState(false);

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

  const likeIconStyles = liked
    ? { backgroundColor: "gray.700", borderRadius: "full" }
    : {};
  const dislikeIconStyles = disliked
    ? { backgroundColor: "gray.700", borderRadius: "full" }
    : {};

  return (
    role === "bot" &&
    kind !== "UPDATE" && (
      <HStack gap={1}>
        {/* Like Button */}
        <HStack
          sx={{ ...messageActionStyles, ...likeIconStyles }}
          w={7}
          h={7}
          align="center"
          cursor="pointer"
          justify="center"
          onClick={() => {
            setLiked(!liked); // Toggle like state
            if (disliked) setDisliked(false); // Reset dislike state if it's active
          }}
        >
          <Icon
            as={AiOutlineLike}
            stroke="gray.200"
            strokeWidth={4}
            fontSize="md"
          />
        </HStack>

        {/* Dislike Button */}
        <HStack
          sx={{ ...messageActionStyles, ...dislikeIconStyles }}
          w={7}
          h={7}
          align="center"
          cursor="pointer"
          justify="center"
          onClick={() => {
            setDisliked(!disliked); // Toggle dislike state
            if (liked) setLiked(false); // Reset like state if it's active
          }}
        >
          <Icon
            as={AiOutlineDislike}
            stroke="gray.200"
            strokeWidth={4}
            fontSize="md"
          />
        </HStack>

        {/* Download Button (for table type) */}
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

        {/* Save Button */}
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

        {/* Tooltip with Query Information */}
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
