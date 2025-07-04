import {
  VStack,
  Icon,
  Box,
  Button,
  useToast,
  HStack,
  Text,
} from "@chakra-ui/react";
import { GoSidebarCollapse } from "react-icons/go";
import { useForm } from "src/helpers/parameter-renderer/hooks";
import { ChakraFormRenderer } from "src/helpers/parameter-renderer/backends";
import { ParameterArray, ParameterForm } from "src/helpers/parameter-spec/src/Index";
import { useEffect, useMemo, useState } from "react";
import { BACKEND_URL } from "src/config";

type AddQueryProps = {
  navOpen: boolean;
  setNavOpen: (arg: (prev: boolean) => boolean) => void;
};

type QueryForm = {
  id: string;
  name: string;
  initial: any;
  list: [any];
  [key: string]: any;
};

type StoredDynamicParam = {
  _internalId: string;
  id: string;
  label: string;
  type: string;
  initial: any;
  list?: {};
};

const AddQuery = ({
  navOpen,
  setNavOpen,
}: AddQueryProps) => {

  const toast = useToast({ position: "bottom-right" });
  const formParameters = useMemo((): ParameterForm<QueryForm> => [{
    label: "",
    required: false,
    parameters: [
      {
        id: "query",
        label: "Query",
        required: true,
        placeholder: "SQL Query",
        type: "string",
        initial: "",
        extraProps: { width: "700px" },
        long: true,
      },{
        id: "query_name",
        label: "Query Name",
        required: true,
        placeholder: "Name",
        type: "string",
        initial: "",
      },{
        id: "query_description",
        label: "Query Description",
        placeholder: "A short description for the query",
        required: true,
        type: "string",
        initial: "",
        long: true,
      },{
        id: "query_id",
        label: "Query Id (Optional)",
        placeholder: "Query Id",
        required: false,
        type: "string",
        extraProps: { width: "400px" },
        initial: "",
      },{
        id: "query_type",
        label: "Query Type",
        required: false,
        type: "enum",
        list: { static: "static", dynamic: "dynamic" },
        initial: "static",
      },{
        id: "user_emails",
        label: "User Emails to share with (comma-separated)",
        required: false,
        type: "list",
        initial: [],
        extraProps: { width: "250px" },
        delimiters: [","],
      }
    ]
  }], []);

  const formControl = useForm({
    parameters: formParameters,
  });

  const [addedParamsList, setAddedParamsList] = useState<StoredDynamicParam[]>([]);

  const [typeSpecificParams, setTypeSpecificParams] = useState<ParameterArray<QueryForm>>([]);

  const dynamicFormParameter = useMemo((): ParameterForm<QueryForm> => [{
    label: "",
    required: false,
    parameters: [
      {
        id: "id",
        label: "Parameter Id",
        required: true,
        placeholder: "Id should be the same as in the query",
        type: "string",
        extraProps: { width: "300px" },
      },{
        id: "label",
        label: "Parameter Label",
        required: true,
        placeholder: "Parameter Label",
        type: "string",
        extraProps: { width: "300px" },
      },{
        id: "type",
        label: "Parameter Type",
        required: true,
        type: "enum",
        initial: "int",
        list: {
          "int": "int",
          "float": "float",
          "string": "string",
          "list": "list",
          "boolean": "boolean",
          "enum": "enum",
          "enum_multi": "enum_multi",
          "date": "date",
          "time": "time",
          "datetime-local": "datetime-local",
        },
      },
      ...typeSpecificParams
    ]
  }], [typeSpecificParams]);

  const paramFormControl = useForm({
    parameters: dynamicFormParameter,
  });

  useEffect(() => {
    const selectedType = paramFormControl.ctx.form.type;
    if (selectedType === 'int' || selectedType === 'float') {
      setTypeSpecificParams([
        {
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: selectedType,
        }
      ]);
    } else if (
      selectedType === 'string' ||
      selectedType === 'date' ||
      selectedType === 'time' ||
      selectedType === 'datetime-local'
    ) {
      setTypeSpecificParams([
        {
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: selectedType,
        }
      ]);
    } else if (selectedType === 'enum') {
      setTypeSpecificParams([
        {
          id: `list_${selectedType}`,
          label: "Enum Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        },{
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: "string",
        }
      ]);
    } else if (selectedType === 'enum_multi') {
      setTypeSpecificParams([
        {
          id: `list_${selectedType}`,
          label: "Enum Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        },{
          id: `initial_${selectedType}`,
          label: "Initial Options (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        }
      ]);
    } else if (selectedType === 'boolean') {
      setTypeSpecificParams([
        {
          id: `initial_${selectedType}`,
          label: "Initial Value",
          required: true,
          type: "enum",
          list: {"true": "true", "false": "false"},
        }
      ]);
    } else if (selectedType === 'list') {
      setTypeSpecificParams([
        {
          id: `initial_${selectedType}`,
          label: "Initial List Values (comma-separated)",
          required: true,
          type: "list",
          delimiters: [","],
        }
      ]);
    }
    else {
      setTypeSpecificParams([]);
    }

  }, [paramFormControl.ctx.form.type]);

  const handleAdd = async () => {
    const paramData = paramFormControl.ctx.form;
    const newParam: StoredDynamicParam = {
      _internalId: `param-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
      id: paramData.id || "id",
      label: paramData.label,
      type: paramData.type,
      initial: paramData[`initial_${paramData.type}`],
      list: Object.fromEntries(
        (paramData[`list_${paramData.type}`] || [])
          .map((item: string) => [item, item])
      ) || {},
    };
    setAddedParamsList((prev) => [...prev, newParam]);
  };

  const handleDeleteParam = (_internalId: string) => {
    setAddedParamsList(
      (prev) => prev
        .filter((param) => param._internalId !== _internalId)
    );
  };

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
        setTypeSpecificParams([]);
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

  const renderAddedParams = () => {
    return addedParamsList.length === 0 ? (
      <Text color="gray.500" mb={4}>No dynamic parameters added yet.</Text>
    ) : (
      <VStack
        w="100%"
        align="start"
        spacing={3}
        mb={6}
        border="1px"
        borderColor="gray.700"
        p={4}
        borderRadius="md"
      >
        {addedParamsList.map((param, index) => (
          <HStack
            key={param._internalId}
            w="100%"
            justifyContent="space-between"
            alignItems="center"
            p={2}
            bg="gray.800"
            borderRadius="md"
          >
            <Box>
              <Text fontWeight="bold" color="white">
                {index + 1}. {param.label || param.id}
              </Text>
              <VStack
                align="start"
                spacing={0}
                color="gray.400"
              >
                <Text as="span" fontWeight="semibold">
                  Id: {param.id}
                </Text>

                <Text as="span" fontWeight="semibold">
                  Type: {param.type}
                </Text>

                {(param.initial !== undefined && param.initial !== null) && (
                  <Text as="span" fontWeight="semibold">
                    Initial: {
                      Array.isArray(param.initial) ?
                        param.initial.join(', ') : String(param.initial)
                    }
                  </Text>
                )}

                {param.list && typeof param.list === 'object' &&
                  Object.keys(param.list).length > 0 && (
                    <Text as="span" fontWeight="semibold">
                      Options: {`${Object.keys(param.list).join(', ')}`}
                    </Text>
                  )}
              </VStack>
            </Box>
            <Button
              size="sm"
              colorScheme="red"
              variant="outline"
              onClick={() => handleDeleteParam(param._internalId)}
            >
              Delete
            </Button>
          </HStack>
        ))}
      </VStack>
    )
  }

  const renderParamForm = () => {
    if (formControl.ctx.form.query_type === 'static') {
      return null;
    }

    return (
      <VStack w="100%" align="start" mt={6}>
        <Box w="100%" fontSize="2xl" fontWeight="bold" textAlign="left" mb={4}>
          Added Dynamic Parameters
        </Box>

        {renderAddedParams()}

        <ChakraFormRenderer ctx={paramFormControl.ctx} />
        <Button
          justifyContent={"space-between"}
          marginBottom={12}
          gap={2}
          color="gray.400"
          bg="gray.700"
          _hover={{ bg: "gray.600", color: "gray.400" }}
          onClick={handleAdd}
        >
          Add
        </Button>
      </VStack>
    )
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
        {renderParamForm()}
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
