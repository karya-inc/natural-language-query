import { Text } from "@chakra-ui/react";
import { AgGridReact } from "ag-grid-react";
import { themeQuartz, colorSchemeDarkBlue, ColDef } from "ag-grid-community";
import { AllCommunityModule, ModuleRegistry } from "ag-grid-community";
import { useMemo } from "react";

ModuleRegistry.registerModules([AllCommunityModule]);

export type ChatTableProps = {
  data: Record<string, unknown>[];
  isLoading?: boolean;
  columnOrder?: string[];
};

const ChatTable = (props: ChatTableProps) => {
  const { data, isLoading, columnOrder = Object.keys(data) } = props;

  // Compute the column definitions based on the column order
  const colDefs = useMemo(() => {
    return columnOrder.map<ColDef>((columnName) => ({
      field: columnName,
      filter: true,
    }));
  }, [columnOrder]);

  const rowData = data;
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
