import { Text } from "@chakra-ui/react";
import { AgGridReact } from "ag-grid-react";
import { themeQuartz, colorSchemeDarkBlue } from "ag-grid-community";
import {
  AllCommunityModule,
  ModuleRegistry,
  SizeColumnsToContentStrategy,
} from "ag-grid-community";
import { useMemo } from "react";

ModuleRegistry.registerModules([AllCommunityModule]);

const ChatTable = ({ data }: { data: Record<string, unknown>[] }) => {
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

  const autoSizeStrategy: SizeColumnsToContentStrategy = useMemo(() => {
    return {
      type: "fitCellContents",
    };
  }, []);

  return rowData.length > 0 ? (
    <AgGridReact
      rowData={rowData}
      columnDefs={colDefs}
      defaultColDef={defaultColDef}
      theme={myTheme}
      domLayout="autoHeight"
      autoSizeStrategy={autoSizeStrategy}
      pagination={pagination}
      paginationPageSize={paginationPageSize}
      paginationPageSizeSelector={paginationPageSizeSelector}
    />
  ) : (
    <Text py={2}>No results match your query. Please be specific</Text>
  );
};

export default ChatTable;
