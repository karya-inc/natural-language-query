// Copyright (c) DAIA Tech Pvt Ltd
//
// Download objects as JSON

import Papa from "papaparse";

export function downloadObjectAs(
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  exportObj: string | object | Array<any>,
  exportName: string,
  type: "json" | "plain" | "csv"
) {
  const downloadAnchorNode = document.createElement("a");
  let serializedData: string;
  switch (type) {
    case "plain":
      if (typeof exportObj === "string") {
        serializedData = exportObj;
      } else {
        throw new Error(
          "Plain download requires a pre-serialized string as input"
        );
      }
      break;

    case "json":
      serializedData = JSON.stringify(exportObj, null, 2);
      break;

    case "csv":
      if (exportObj instanceof Array) {
        serializedData = Papa.unparse(exportObj);
      } else {
        throw new Error(
          "CSV download requires the exported object to be an array"
        );
      }
      break;
    default:
      throw new Error("Cannot download unsupported filetype");
  }
  const dataStr =
    `data:text/${type};charset=utf-8,` + encodeURIComponent(serializedData);
  downloadAnchorNode.setAttribute("href", dataStr);
  downloadAnchorNode.setAttribute("download", exportName);
  document.body.appendChild(downloadAnchorNode);
  downloadAnchorNode.click();
  downloadAnchorNode.remove();
}

export const messageActionStyles = {
  ":hover": {
    backgroundColor: "gray.700",
    rounded: "lg",
  },
};

export const handleDownload = (report: Record<string, string>[]) => {
  const today = new Date();
  const date = today.getDate();
  const month = today.getMonth() + 1;
  const year = today.getFullYear();
  downloadObjectAs(report, `Table-${year}-${month}-${date}.csv`, "csv");
};
