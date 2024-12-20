import {
  Button,
  ButtonGroup,
  FocusLock,
  FormControl,
  FormLabel,
  HStack,
  Icon,
  IconButton,
  Input,
  Popover,
  PopoverArrow,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Stack,
  Tooltip,
  useDisclosure,
} from "@chakra-ui/react";
import { FaRegSave } from "react-icons/fa";
import { IoInformationCircleOutline } from "react-icons/io5";
import { LuDownloadCloud } from "react-icons/lu";
import { AiOutlineLike } from "react-icons/ai";
import { AiOutlineDislike } from "react-icons/ai";
import { downloadObjectAs } from "../pages/Chat/utils";
import { Message } from "../pages/Chat";
import { useState, useRef, forwardRef, useContext } from "react";
import useNavBar from "./NavBar/useNavBar";
import { BACKEND_URL } from "../config";
import { SavedQueryContext } from "../layouts/RootLayout";

interface TextInputProps {
  label: string;
  id: string;
  defaultValue?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const ChatActions = ({ msg }: { msg: Message }) => {
  const { message, role, type, kind, query, sql_query_id, turn_id } = msg;
  const [liked, setLiked] = useState(false);
  const [disliked, setDisliked] = useState(false);
  const { onOpen, onClose, isOpen } = useDisclosure();
  const firstFieldRef = useRef(null);

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
            setLiked(!liked);
            if (disliked) setDisliked(false);
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
            setDisliked(!disliked);
            if (liked) setLiked(false);
          }}
        >
          <Icon
            as={AiOutlineDislike}
            stroke="gray.200"
            strokeWidth={4}
            fontSize="md"
          />
        </HStack>

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
              onClick={() => {
                if (Array.isArray(message)) {
                  handleDownload(message as Record<string, string>[]);
                }
              }}
            />
          </HStack>
        )}

        <Popover
          isOpen={isOpen}
          initialFocusRef={firstFieldRef}
          onOpen={onOpen}
          onClose={onClose}
          placement="top"
          closeOnBlur={false}
        >
          <PopoverTrigger>
            <IconButton
              size="sm"
              bg="none"
              color="gray.400"
              sx={messageActionStyles}
              icon={
                <HStack
                  w={7}
                  h={7}
                  align="center"
                  cursor="pointer"
                  justify="center"
                >
                  <Icon
                    as={FaRegSave}
                    stroke="gray.100"
                    strokeWidth={4}
                    fontSize="md"
                  />
                </HStack>
              }
              aria-label={"Save the query"}
            />
          </PopoverTrigger>
          <PopoverContent
            p={5}
            bg={"gray.700"}
            border="1px solid"
            borderColor={"gray.700"}
          >
            <FocusLock persistentFocus={false}>
              <PopoverArrow bg={"gray.700"} />
              <PopoverCloseButton />
              <Form
                firstFieldRef={firstFieldRef}
                onCancel={onClose}
                sql_query_id={sql_query_id}
                turn_id={turn_id}
              />
            </FocusLock>
          </PopoverContent>
        </Popover>

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

const TextInput = forwardRef<HTMLInputElement, TextInputProps>((props, ref) => {
  return (
    <FormControl>
      <FormLabel htmlFor={props.id}>{props.label}</FormLabel>
      <Input ref={ref} {...props} />
    </FormControl>
  );
});

const Form = ({
  firstFieldRef,
  onCancel,
  sql_query_id,
  turn_id,
}: {
  firstFieldRef: React.RefObject<HTMLInputElement>;
  onCancel: () => void;
  sql_query_id?: string;
  turn_id?: string;
}) => {
  const { savedQueryDetails, setSavedQueryDetails } =
    useContext(SavedQueryContext);

  const { title, description } = savedQueryDetails;
  const { postSavedQuery } = useNavBar(title, description);

  function handleSave() {
    postSavedQuery(`${BACKEND_URL}/save_query/${turn_id}/${sql_query_id}`);
    onCancel();
    setSavedQueryDetails({ title: "", description: "", sql_query_id: "" });
  }

  return (
    <Stack spacing={4}>
      <TextInput
        label="Title"
        id="title"
        ref={firstFieldRef}
        value={title}
        onChange={(e) =>
          setSavedQueryDetails({ ...savedQueryDetails, title: e.target.value })
        }
      />
      <TextInput
        label="Description"
        id="description"
        value={description}
        onChange={(e) =>
          setSavedQueryDetails({
            ...savedQueryDetails,
            description: e.target.value,
          })
        }
      />
      <ButtonGroup display="flex" justifyContent="flex-end">
        <Button
          variant="solid"
          onClick={() => {
            onCancel();
            setSavedQueryDetails({
              title: "",
              description: "",
              sql_query_id: "",
            });
          }}
        >
          Cancel
        </Button>
        <Button colorScheme="teal" onClick={handleSave}>
          Save
        </Button>
      </ButtonGroup>
    </Stack>
  );
};

export default ChatActions;
