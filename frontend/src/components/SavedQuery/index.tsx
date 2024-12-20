import { VStack, Text, Box, Button } from "@chakra-ui/react";
import { useContext, useState } from "react";
import { SavedQueryContext } from "../../layouts/RootLayout";
import { BACKEND_URL } from "../../config";
import ChatTable from "../ChatTable";

const SavedQuery = () => {
  const { savedQueryDetails } = useContext(SavedQueryContext);
  const [data, setData] = useState([]);

  const handleExecute = async () => {
    try {
      const response1 = await fetch(
        `${BACKEND_URL}/queries/${savedQueryDetails.sql_query_id}/execution`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
        }
      );

      if (!response1.ok) {
        throw new Error("Failed to execute query");
      }

      const result = await response1.json();
      let executionStatus = "RUNNING";
      let resultData = null;

      while (executionStatus === "RUNNING") {
        const response2 = await fetch(
          `${BACKEND_URL}/execution_result/${result.id}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
          }
        );

        if (!response2.ok) {
          throw new Error("Failed to fetch execution result");
        }

        const result2 = await response2.json();
        executionStatus = result2.execution_log.status;
        resultData = result2.result;

        if (executionStatus === "RUNNING") {
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }
      }

      if (executionStatus === "SUCCESS") {
        console.log("Query executed successfully:", resultData);
        setData(resultData || []);
      } else {
        console.error("Query execution failed");
      }
    } catch (error) {
      console.error("Error executing query:", error);
    }
  };

  return (
    <VStack
      bg="gray.900"
      align="start"
      spacing={6}
      w="100%"
      h="100vh"
      p={8}
      color="white"
    >
      {/* Title Section */}
      <Box w="100%" textAlign="left">
        <Text fontSize="2xl" fontWeight="bold">
          {savedQueryDetails.title || "Untitled Query"}
        </Text>
      </Box>

      {/* Description Section */}
      {savedQueryDetails.description && (
        <Box w="100%">
          <Text fontSize="lg" color="gray.300">
            {savedQueryDetails.description}
          </Text>
        </Box>
      )}

      {/* Execute Button */}
      {data.length > 0 ? (
        <ChatTable data={data} />
      ) : (
        <Box w="100%" textAlign="left">
          <Button colorScheme="teal" size="lg" onClick={handleExecute}>
            Execute Query
          </Button>
        </Box>
      )}
    </VStack>
  );
};

export default SavedQuery;
