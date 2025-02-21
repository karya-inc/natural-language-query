import { VStack, Text, Box, Button, Icon } from "@chakra-ui/react";
import { BACKEND_URL } from "../../config";
import ChatTable from "../ChatTable";
import { GoSidebarCollapse } from "react-icons/go";
import { useEffect, useState } from "react";
import { FetchingSkeleton } from "../../pages/Chat";
import { SavedQueryDataInterface } from "../NavBar/useNavBar";
import { IoCloudDownloadOutline } from "react-icons/io5";
import { RiLoopRightFill } from "react-icons/ri";
import { handleDownload } from "../../pages/Chat/utils";

type SavedQueryProps = {
  savedQueryData: SavedQueryDataInterface;
  navOpen: boolean;
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
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

  useEffect(() => {
    getSavedTableData();
  }, [savedQueryData.sql_query_id]);

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

  async function getSavedTableData() {
    try {
      setIsFetching(true);
      const response = await fetch(
        `${BACKEND_URL}/queries/${savedQueryData.sql_query_id}/execution`,
        {
          method: "GET",
          credentials: "include",
        }
      );
      const { id } = await response.json();
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
      console.error("Error fetching data:", error);
    } finally {
      setIsFetching(false);
    }
  }

  return (
    <VStack
      bg="gray.900"
      align="start"
      gap={6}
      w="100%"
      h="100%"
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
              onClick={() => setTimeout(handleExecute)}
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
                    savedQueryTableData as unknown as Record<string, string>[]
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
        {isFetching ? (
          <FetchingSkeleton />
        ) : (
          savedQueryTableData.length > 0 && (
            <ChatTable data={savedQueryTableData} />
          )
        )}
      </VStack>
    </VStack>
  );
};

export default SavedQuery;
