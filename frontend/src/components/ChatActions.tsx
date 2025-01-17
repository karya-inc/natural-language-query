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
import { IoCloudDownloadOutline } from "react-icons/io5";
import { AiOutlineLike } from "react-icons/ai";
import { AiOutlineDislike } from "react-icons/ai";
import { handleDownload, messageActionStyles } from "../pages/Chat/utils";
import { Message } from "../pages/Chat";
import { useState, useRef, forwardRef, useContext } from "react";
import useNavBar from "./NavBar/useNavBar";
import { BACKEND_URL } from "../config";
import { SavedQueryContext, SavedQueryDataInterface } from "./NavBar/utils";
import { InputProps } from "@chakra-ui/react";

interface TextInputProps extends InputProps {
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
            bg={"#2a2d3d"}
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
      <FormLabel htmlFor={props.id} fontWeight={"bold"}>
        {props.label}
      </FormLabel>
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
  const [queryDetails, setQueryDetails] = useState({
    name: "",
    description: "",
    sql_query_id,
  });
  const { name, description } = queryDetails;
  const { saveQuery } = useNavBar(name, description);
  const { setSavedQueries } = useContext(SavedQueryContext);

  function handleSave() {
    setSavedQueries((prev: SavedQueryDataInterface[]) => [
      queryDetails as SavedQueryDataInterface,
      ...prev,
    ]);
    saveQuery(`${BACKEND_URL}/save_query/${turn_id}/${sql_query_id}`);
    onCancel();
    setQueryDetails({ name: "", description: "", sql_query_id: "" });
  }

  return (
    <Stack spacing={4}>
      <TextInput
        label="Title"
        id="name"
        ref={firstFieldRef}
        value={name}
        onChange={(e) =>
          setQueryDetails({ ...queryDetails, name: e.target.value })
        }
        _focusVisible={{ boxShadow: "none", borderColor: "gray.500" }}
        borderColor="gray.500"
      />
      <TextInput
        label="Description"
        id="description"
        value={description}
        onChange={(e) =>
          setQueryDetails({
            ...queryDetails,
            description: e.target.value,
          })
        }
        _focusVisible={{ boxShadow: "none", borderColor: "gray.500" }}
        borderColor="gray.500"
      />
      <ButtonGroup display="flex" justifyContent="flex-end">
        <Button
          variant="unstyled"
          px={4}
          onClick={() => {
            onCancel();
            setQueryDetails({
              name: "",
              description: "",
              sql_query_id: "",
            });
          }}
        >
          Cancel
        </Button>
        <Button colorScheme="gray" background={"gray.300"} onClick={handleSave}>
          Save
        </Button>
      </ButtonGroup>
    </Stack>
  );
};

export default ChatActions;
