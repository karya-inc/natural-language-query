import { VStack, Text, Box, Button, Icon } from "@chakra-ui/react";
import { BACKEND_URL } from "../../config";
import ChatTable from "../ChatTable";
import { GoSidebarCollapse } from "react-icons/go";
import { useState } from "react";
import { FetchingSkeleton } from "../../pages/Chat";

type SavedQueryProps = {
  savedQueryData: {
    title: string;
    description: string;
    sql_query_id: string;
  };
  navOpen: boolean;
  setNavOpen: (arg: boolean) => void;
  getSavedQueryTableData: (arg: string) => Promise<{
    execution_log: { status: string };
    result: Record<string, unknown>[];
  }>;
  postQueryToGetId: (arg: string) => Promise<string>;
  savedQueryTableData: Record<string, unknown>[];
  setSavedQueryTableData: (arg: Record<string, unknown>[]) => void;
};

const SavedQuery = ({
  savedQueryData,
  navOpen,
  setNavOpen,
  getSavedQueryTableData,
  postQueryToGetId,
  savedQueryTableData,
  setSavedQueryTableData,
}: SavedQueryProps) => {
  const [isFetching, setIsFetching] = useState(false);

  const handleExecute = async () => {
    try {
      setIsFetching(true);
      const id = await postQueryToGetId(
        `${BACKEND_URL}/queries/${savedQueryData.sql_query_id}/execution`
      );
      let executionStatus = "RUNNING";
      let resultData: Record<string, unknown>[] = [];
      while (executionStatus === "RUNNING") {
        const { execution_log, result } = await getSavedQueryTableData(
          `${BACKEND_URL}/execution_result/${id}`
        );
        executionStatus = execution_log?.status;
        resultData = result;
      }
      if (executionStatus === "SUCCESS") {
        setSavedQueryTableData(resultData || []);
      }
    } catch (error) {
      console.error("Error executing query:", error);
    } finally {
      setIsFetching(false);
    }
  };

  return (
    <VStack
      bg="gray.900"
      align="start"
      gap={6}
      w="100%"
      h="100vh"
      p={8}
      color="white"
    >
      {!navOpen && (
        <Icon
          as={GoSidebarCollapse}
          stroke="gray.400"
          strokeWidth={1}
          fontSize="xl"
          cursor="pointer"
          onClick={() => setNavOpen(!navOpen)}
          position="absolute"
          top={5}
          left={5}
        />
      )}
      <VStack w="full" px={{ base: "2.5vw", xl: "5vw" }} align="start" gap={4}>
        {savedQueryData.title && (
          <Box w="100%" textAlign="left">
            <Text fontSize="2xl" fontWeight="bold">
              {savedQueryData.title || "Untitled Query"}
            </Text>
          </Box>
        )}
        {savedQueryData.description && (
          <Box w="100%">
            <Text fontSize="lg" color="gray.300">
              {savedQueryData.description}
            </Text>
          </Box>
        )}
        {isFetching ? (
          <FetchingSkeleton />
        ) : savedQueryTableData.length > 0 ? (
          <ChatTable data={savedQueryTableData} />
        ) : (
          <Box w="100%" textAlign="left">
            <Button
              color="gray.400"
              bg="gray.700"
              _hover={{ bg: "gray.600", color: "gray.400" }}
              onClick={() => setTimeout(handleExecute)}
            >
              Execute
            </Button>
          </Box>
        )}
      </VStack>
    </VStack>
  );
};

export default SavedQuery;
