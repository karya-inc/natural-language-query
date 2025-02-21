import {
  VStack,
  Text,
  Box,
  Button,
  Icon,
  Divider,
  useToast,
} from "@chakra-ui/react";
import { BACKEND_URL } from "../../config";
import ChatTable from "../ChatTable";
import { GoSidebarCollapse } from "react-icons/go";
import { useEffect, useState } from "react";
import {
  ExecutionLog,
  ExecutionResponse,
  SavedQueryDataInterface,
} from "../NavBar/useNavBar";
import { IoCloudDownloadOutline } from "react-icons/io5";
import { RiLoopRightFill } from "react-icons/ri";
import { handleDownload } from "../../pages/Chat/utils";

type SavedQueryProps = {
  savedQueryData: SavedQueryDataInterface;
  navOpen: boolean;
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
  getExecutionResponseById: (
    url: string,
  ) => Promise<ExecutionResponse | undefined>;
  executeSavedQueryByQueryId: (
    sql_id: string,
  ) => Promise<ExecutionLog | undefined>;
  savedQueryTableData: Record<string, unknown>[];
  setSavedQueryTableData: (arg: Record<string, unknown>[]) => void;
};

const SavedQuery = ({
  savedQueryData,
  navOpen,
  setNavOpen,
  getExecutionResponseById,
  executeSavedQueryByQueryId,
  savedQueryTableData,
  setSavedQueryTableData,
}: SavedQueryProps) => {
  const [isFetching, setIsFetching] = useState(false);
  const [executionResponse, setExecutionResponse] =
    useState<ExecutionResponse | null>(null);

  const [lastExecutedAt, setLastExecutedAt] = useState<string | null>(null);

  const toast = useToast({ position: "bottom-right" });

  useEffect(() => {
    getSavedTableData();
  }, [savedQueryData.sql_query_id]);

  useEffect(() => {
    if (!executionResponse || !executionResponse.execution_log.id) {
      return;
    }

    // Poll the execution response if the status is running
    if (
      ["RUNNING", "PENDING"].includes(executionResponse.execution_log.status)
    ) {
      const timeoutHandler = setTimeout(() => {
        refetchExecutionResponse(executionResponse.execution_log.id);
      }, 2000);

      return () => {
        clearTimeout(timeoutHandler);
      };
    }

    const { execution_log, result } = executionResponse;

    // Update the table data and last executed time
    if (execution_log.status === "SUCCESS") {
      setSavedQueryTableData(result ?? []);
      setLastExecutedAt(execution_log.completed_at);
      setIsFetching(false);
      return;
    }

    // Log error if execution failed
    if (execution_log.status === "FAILED") {
      console.error("Error executing query:", execution_log.logs);
      toastExecutionFailure();
      setIsFetching(false);
    }
  }, [executionResponse]);

  /** Show Toast To User When Execution Fails */
  const toastExecutionFailure = () => {
    toast({
      title: "Failed to execute query",
      description:
        "Something went wrong while executing the query. Please try again later.",
      status: "error",
    });
  };

  /** Refetch and update the execution response for an execution log*/
  const refetchExecutionResponse = async (execution_id: string) => {
    const updatedExecutionResponse = await getExecutionResponseById(
      `${BACKEND_URL}/execution_result/${execution_id}`,
    );
    if (updatedExecutionResponse) {
      setExecutionResponse(updatedExecutionResponse);
    } else {
      setIsFetching(false);
    }
    return updatedExecutionResponse;
  };

  /** Execute Handler - Refresh the report to get the latest data */
  const handleExecute = async () => {
    try {
      setIsFetching(true);
      const execution_log = await executeSavedQueryByQueryId(
        `${BACKEND_URL}/queries/${savedQueryData.sql_query_id}/execution`,
      );
      if (!execution_log) {
        toastExecutionFailure();
        return;
      }
      setExecutionResponse({ execution_log });
    } catch (error) {
      console.error("Error executing query:", error);
    }
  };

  /** Fetch the details of the last successful execution response */
  async function getSavedTableData() {
    try {
      setIsFetching(true);
      const response = await fetch(
        `${BACKEND_URL}/queries/${savedQueryData.sql_query_id}/execution`,
        {
          method: "GET",
          credentials: "include",
        },
      );
      const execution_log: ExecutionLog = await response.json();
      if (!execution_log.id) {
        return;
      }
      const executionResponse = await refetchExecutionResponse(
        execution_log.id,
      );
      if (executionResponse) {
        setExecutionResponse(executionResponse);
      }
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setIsFetching(false);
    }
  }

  const hasData = savedQueryTableData.length > 0;

  return (
    <VStack
      bg="gray.900"
      align="start"
      gap={6}
      w="100%"
      h="100%"
      p={8}
      color="white"
      overflowY="auto"
    >
      {!navOpen && (
        <Icon
          as={GoSidebarCollapse}
          stroke="gray.400"
          strokeWidth={1}
          fontSize="xl"
          cursor="pointer"
          onClick={() => setNavOpen((prev: boolean) => !prev)}
          position="absolute"
          top={5}
          left={5}
        />
      )}
      <VStack
        w="full"
        px={{ base: "2.5vw", xl: "5vw" }}
        align="start"
        gap={4}
        color={"gray.400"}
      >
        {savedQueryData.name && (
          <Box w="100%" textAlign="left">
            <Text fontSize="2xl" fontWeight="bold">
              {savedQueryData.name}
            </Text>
          </Box>
        )}
        {lastExecutedAt && (
          <Text fontSize="sm" color="gray.300" fontStyle="italic">
            <strong>Last Updated At: </strong>
            {new Date(lastExecutedAt).toLocaleString(undefined, {
              dateStyle: "long",
              timeStyle: "short",
            })}
          </Text>
        )}
        <Divider />
        {savedQueryData.description && (
          <Box w="100%">
            <Text fontSize="lg" color="gray.300">
              {savedQueryData.description}
            </Text>
          </Box>
        )}
        {savedQueryTableData.length >= 0 && (
          <Box w="100%" display="flex" gap={4}>
            <Button
              justifyContent={"space-between"}
              gap={2}
              color="gray.400"
              bg="gray.700"
              _hover={{ bg: "gray.600", color: "gray.400" }}
              onClick={handleExecute}
              isDisabled={isFetching}
              isLoading={isFetching && hasData}
            >
              Execute
              <Icon
                as={RiLoopRightFill}
                stroke="gray.400"
                strokeWidth={0}
                fontSize="md"
              />
            </Button>
            <Button
              justifyContent={"space-between"}
              gap={2}
              cursor="pointer"
              color="gray.400"
              bg="gray.700"
              _hover={{ bg: "gray.600", color: "gray.400" }}
              onClick={() => {
                if (Array.isArray(savedQueryTableData)) {
                  handleDownload(
                    savedQueryTableData as unknown as Record<string, string>[],
                  );
                }
              }}
            >
              <Text fontSize={"sm"}>Download</Text>
              <Icon
                as={IoCloudDownloadOutline}
                stroke="gray.400"
                strokeWidth={2}
                fontSize="md"
              />
            </Button>
          </Box>
        )}
        {savedQueryTableData.length > 0 && (
          <Box width="100%">
            <ChatTable data={savedQueryTableData} isLoading={isFetching} />
          </Box>
        )}
      </VStack>
    </VStack>
  );
};

export default SavedQuery;
