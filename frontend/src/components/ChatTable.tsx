import { Text } from "@chakra-ui/react";
import { AgGridReact } from "ag-grid-react";
import { themeQuartz, colorSchemeDarkBlue } from "ag-grid-community";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";

ModuleRegistry.registerModules([AllCommunityModule]);

const ChatTable = ({
  data,
  isLoading,
}: {
  data: Record<string, unknown>[];
  isLoading?: boolean;
}) => {
  const rowData = data;
  const colDefs = Object.keys(rowData[0]).map((key) => ({
    field: key,
    filter: true,
  }));
  const defaultColDef = {
    flex: 1,
  };
  const pagination = true;
  const paginationPageSize = 10;
  const paginationPageSizeSelector = [10, 20, 40];
  const myTheme = themeQuartz.withPart(colorSchemeDarkBlue).withParams({
    backgroundColor: "rgb(42, 45, 61)",
    accentColor: "lightblue",
  });

  return rowData.length > 0 ? (
    <AgGridReact
      loading={isLoading}
      rowData={rowData}
      columnDefs={colDefs}
      defaultColDef={defaultColDef}
      theme={myTheme}
      domLayout="autoHeight"
      pagination={pagination}
      paginationPageSize={paginationPageSize}
      paginationPageSizeSelector={paginationPageSizeSelector}
    />
  ) : (
    <Text py={2}>No results match your query. Please be specific</Text>
  );
};

export default ChatTable;
