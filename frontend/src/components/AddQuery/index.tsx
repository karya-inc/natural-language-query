import {
  VStack,
  Icon,
  Box,
  Button,
  useToast,
} from "@chakra-ui/react";
import { GoSidebarCollapse } from "react-icons/go";
import { useForm } from "src/helpers/parameter-renderer/hooks";
import { ChakraFormRenderer } from "src/helpers/parameter-renderer/backends";
import { ParameterForm } from "src/helpers/parameter-spec/src/Index";
import { useMemo, useState } from "react";
import { BACKEND_URL } from "src/config";
import { buildQueryForm, QueryForm, StoredDynamicParam } from "./formSpec";
import DynamicParamForm from "./dynamicParamForm";

type AddQueryProps = {
  navOpen: boolean;
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
};

const AddQuery = ({
  navOpen,
  setNavOpen,
}: AddQueryProps) => {

  const toast = useToast({ position: "bottom-right" });
  const [addedParamsList, setAddedParamsList] = useState<StoredDynamicParam[]>([]);
  const formParameters = useMemo((): ParameterForm<QueryForm> => buildQueryForm(), []);
  const formControl = useForm({
    parameters: formParameters,
  });

  const handleSubmit = async () => {
    try {
      const query_data = formControl.ctx.form;
      const params_data = addedParamsList
        .map(({ _internalId, ...rest }) => rest) || [];
      const response = await fetch(`${BACKEND_URL}/add_query`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            "query_data": query_data,
            "params_data": params_data
          }),
          credentials: "include",
        }
      );

      if (response.status == 200) {
        toast({
          title: "Query added successfully",
          description: "The Query has been added and shared with the specified users",
          status: "success",
        });
        setAddedParamsList([]);
      } else {
        const errorData = await response.json();
        toast({
          title: "Failed to add query",
          description: errorData.detail ? errorData.detail :
            "An unexpected error occurred",
          status: "error",
        });
      }
    } catch (error) {
      console.error("Error adding query:", error);
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
        <Box w="100%" fontSize="2xl" fontWeight="bold" textAlign="left">
          Add Query
        </Box>
        <ChakraFormRenderer ctx={formControl.ctx} />
        {formControl.ctx.form.query_type === 'dynamic' &&
          <DynamicParamForm
            addedParamsList={addedParamsList}
            setAddedParamsList={setAddedParamsList}
          />
        }
        <Box w="100%">
          <Button
            justifyContent={"space-between"}
            gap={2}
            color="gray.400"
            bg="gray.700"
            _hover={{ bg: "gray.600", color: "gray.400" }}
            onClick={handleSubmit}
          >
            Submit
          </Button>
        </Box>
      </VStack>
    </VStack>
  );
};

export default AddQuery;
