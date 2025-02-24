import { Text } from "@chakra-ui/react";
import { AgGridReact } from "ag-grid-react";
import { themeQuartz, colorSchemeDarkBlue, ColDef } from "ag-grid-community";
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
  const colDefs: ColDef[] = Object.keys(rowData[0]).map((key) => ({
    field: key,
    filter: true,
  }));
  const defaultColDef: ColDef = {
    maxWidth: 400,
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
      autoSizeStrategy={{ type: "fitCellContents" }}
      pagination={pagination}
      paginationPageSize={paginationPageSize}
      paginationPageSizeSelector={paginationPageSizeSelector}
    />
  ) : (
    <Text py={2}>No data to show</Text>
  );
};

export default ChatTable;
