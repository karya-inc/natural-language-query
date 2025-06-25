import {
  VStack,
  Text,
  Button,
  Icon,
  useToast,
  Input,
  Popover,
  PopoverTrigger,
  PopoverContent,
  PopoverArrow,
  PopoverCloseButton,
  PopoverBody,
} from "@chakra-ui/react";
import { BACKEND_URL } from "../../config";
import { useState, useRef } from "react";
import { IoShareSocialOutline } from "react-icons/io5";
import { SavedQueryDataInterface } from "../NavBar/useNavBar";

type ShareQueryProps = {
  savedQueryData: SavedQueryDataInterface
}

const ShareQuery = ({
  savedQueryData
}: ShareQueryProps) => {
  
  const initialFocusRef = useRef(null);
  const [isSharing, setIsSharing] = useState(false);
  const [shareInputValue, setShareInputValue] = useState("");
  const toast = useToast({ position: "bottom-right" });

  const handleShareQuery = async () => {
    if (!shareInputValue.trim()) {
      toast({
        title: "No users specified",
        description: "Please enter at least one user email to share with.",
        status: "warning",
      });
      return;
    }

    setIsSharing(true);
    try {
      const userEmails = shareInputValue.split(',')
      .map(id => id.trim())
      .filter(id => id);
      
      const response = await fetch(
        `${BACKEND_URL}/queries/${savedQueryData.sql_query_id}/share`,
        {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ user_emails: userEmails }),
        }
      );

      if (response.ok) {
        toast({
          title: "Query shared successfully",
          description: `The query has been shared with the specified users.`,
          status: "success",
        });
        setShareInputValue("");
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to share query");
      }
    } catch (error) {
      console.error("Error sharing query:", error);
      toast({
        title: "Failed to share query",
        description: error instanceof Error ? error.message : "An unexpected error occurred",
        status: "error",
      });
    } finally {
      setIsSharing(false);
    }
  };

  return (
    <Popover
      initialFocusRef={initialFocusRef}
      placement="top"
      closeOnBlur={true}
    >
      <PopoverTrigger>
        <Button
          justifyContent={"space-between"}
          gap={2}
          cursor="pointer"
          color="gray.400"
          bg="gray.700"
          _hover={{ bg: "gray.600", color: "gray.400" }}
        >
          <Text fontSize={"sm"}>Share</Text>
          <Icon
            as={IoShareSocialOutline}
            stroke="gray.400"
            strokeWidth={2}
            fontSize="md"
          />
        </Button>
      </PopoverTrigger>

      <PopoverContent bg={"#2a2d3d"} borderColor="gray.700" width={400}>
        <PopoverArrow bg={"gray.700"} />
        <PopoverCloseButton />
        <PopoverBody >
          <VStack spacing={4} px={4} py={4}>
            <Text color="gray.400">
              Enter user emails (comma-separated) to share with:
            </Text>
            <Input
              ref={initialFocusRef}
              placeholder="email1, email2, email3"
              value={shareInputValue}
              onChange={(e) => setShareInputValue(e.target.value)}
              bg="gray.700"
              borderColor="gray.500"
              _focusVisible={{ boxShadow: "none", borderColor: "gray.500" }}
            />
            <Button
              colorScheme="gray"
              width="full"
              px={4}
              onClick={handleShareQuery}
              isLoading={isSharing}
              loadingText="Sharing..."
            >
              Share
            </Button>
          </VStack>
        </PopoverBody>
      </PopoverContent>
    </Popover>
  );
};

export default ShareQuery;
