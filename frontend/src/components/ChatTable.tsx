import { Table, Tbody, Td, Th, Thead, Tr, Text } from "@chakra-ui/react";

const ChatTable = ({ data }: { data: string }) => {
  return JSON.parse(data).length > 0 ? (
    <Table size="sm" variant="simple">
      <Thead bg="#2A2D3D" borderBottom="1px solid" borderColor="gray.500">
        <Tr>
          {Object.keys(JSON.parse(data)[0]).map((key) => (
            <Th
              key={key}
              color="gray.500"
              p={3}
              border="1px"
              borderColor="gray.500"
            >
              {key}
            </Th>
          ))}
        </Tr>
      </Thead>
      <Tbody>
        {JSON.parse(data).map((row: Record<string, string>, index: number) => (
          <Tr key={index}>
            {Object.values(row).map((value, colIndex) => (
              <Td key={colIndex} py={5} border="1px" borderColor="gray.500">
                {value}
              </Td>
            ))}
          </Tr>
        ))}
      </Tbody>
    </Table>
  ) : (
    <Text py={2}>No results match your query. Please be specific</Text>
  );
};

export default ChatTable;
