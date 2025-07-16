import {
  VStack,
  Box,
  Button,
  HStack,
  Text,
} from "@chakra-ui/react";
import { useForm } from "src/helpers/parameter-renderer/hooks";
import { ChakraFormRenderer } from "src/helpers/parameter-renderer/backends";
import { ParameterArray, ParameterForm } from "src/helpers/parameter-spec/src/Index";
import { useEffect, useMemo, useState } from "react";
import { buildDynamicParamForm, getTypeSpecificParams } from "./formSpec";
import { QueryForm } from "./formSpec";
import { StoredDynamicParam } from "./formSpec";

type DynamicParamFormProps = {
  addedParamsList: StoredDynamicParam[]
  setAddedParamsList: React.Dispatch<React.SetStateAction<StoredDynamicParam[]>>
}

const DynamicParamForm = ({
  addedParamsList,
  setAddedParamsList
}: DynamicParamFormProps) => {

  const [typeSpecificParams, setTypeSpecificParams] =
    useState<ParameterArray<QueryForm>>([]);
  const dynamicFormParameter = useMemo((): ParameterForm<QueryForm> =>
    buildDynamicParamForm(typeSpecificParams), [typeSpecificParams]
  );
  const paramFormControl = useForm({
    parameters: dynamicFormParameter,
  });

  useEffect(() => {
    const selectedType = paramFormControl.ctx.form.type;
    setTypeSpecificParams(getTypeSpecificParams(selectedType));
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
        (paramData[`list_${paramData.type}`] || []).map((item: string) => [item, item])
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

  return (
    <VStack w="100%" align="start" mt={6}>
      <Box w="100%" fontSize="2xl" fontWeight="bold" textAlign="left" mb={4}>
        Added Dynamic Parameters
      </Box>

      {addedParamsList.length === 0 ? (
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
      )}

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
};

export default DynamicParamForm;
