import { VStack, Text, Box, Button, Icon } from "@chakra-ui/react";
import { BACKEND_URL } from "../../config";
import ChatTable from "../ChatTable";
import { GoSidebarCollapse } from "react-icons/go";
import { useState } from "react";
import { FetchingSkeleton } from "../../pages/Chat";
import { SavedQueryDataInterface } from "../NavBar/useNavBar";
import { Column, RowData } from "@tanstack/react-table";
import { ArrowUpDown } from "lucide-react";

type SavedQueryProps = {
  savedQueryData: SavedQueryDataInterface;
  navOpen: boolean;
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
  getSavedQueryTableData: (arg: string) => Promise<{
    execution_log: { status: string };
    result: string | Record<string, unknown>[];
  }>;
  postQueryToGetId: (arg: string) => Promise<string>;
  savedQueryTableData: string | Record<string, unknown>[];
  setSavedQueryTableData: (arg: string | Record<string, unknown>[]) => void;
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
      let resultData: string | Record<string, unknown>[] = [];
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

  type ColProps = {
    header: ({ column }: { column: Column<RowData> }) => JSX.Element;
    accessorKey: string;
  };

  console.log(savedQueryTableData);

  let colDefs: ColProps[] = [];
  if (savedQueryTableData !== null && savedQueryTableData.length > 0) {
    colDefs = Object.keys(savedQueryTableData[0]).map((key) => ({
      header: ({ column }) => {
        return (
          <Button
            variant="plain"
            size={"md"}
            color={"gray.500"}
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
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
          onClick={() => setNavOpen((prev: boolean) => !prev)}
          position="absolute"
          top={5}
          left={5}
        />
      )}
      <VStack w="full" px={{ base: "2.5vw", xl: "5vw" }} align="start" gap={4}>
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
        {isFetching ? (
          <FetchingSkeleton />
        ) : savedQueryTableData.length > 0 ? (
          <ChatTable
            columns={colDefs}
            data={savedQueryTableData as RowData[]}
          />
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
