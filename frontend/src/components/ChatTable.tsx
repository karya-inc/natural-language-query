"use client";

import { Button } from "../components/ui/button";
import { useState } from "react";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  SortingState,
  ColumnFiltersState,
  getFilteredRowModel,
  getSortedRowModel,
  getPaginationRowModel,
  VisibilityState,
  useReactTable,
} from "@tanstack/react-table";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

import { Input } from "../components/ui/input";
import { HStack, VStack } from "@chakra-ui/react";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
}

export default function ChatTable<TData, TValue>({
  columns,
  data,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    onColumnFiltersChange: setColumnFilters,
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
    },
  });

  return (
    <VStack alignItems={"flex-start"}>
      <Input
        placeholder="Search all..."
        value={table.getState().globalFilter || ""}
        onChange={(event) => table.setGlobalFilter(event.target.value)}
        className="border border-gray-700 w-full"
      />
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id} className="">
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                );
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <TableRow
                key={row.id}
                data-state={row.getIsSelected() && "selected"}
              >
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
      {(table.getCanPreviousPage() || table.getCanNextPage()) && (
        <HStack justify={"flex-end"} w={"full"}>
          <Button
            variant={`${!table.getCanPreviousPage() ? "default" : "secondary"}`}
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
            style={{ backgroundColor: "#2a2d3d", color: "lightgray" }}
          >
            Previous
          </Button>
          <Button
            variant={`${!table.getCanNextPage() ? "default" : "secondary"}`}
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
            style={{ backgroundColor: "#2a2d3d", color: "lightgray" }}
          >
            Next
          </Button>
        </HStack>
      )}
    </VStack>
  );
}
