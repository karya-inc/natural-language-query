import { createContext } from "react";

export const SavedQueryContext = createContext<{
  savedQueryData: {
    name: string;
    description: string;
    sql_query_id: string;
  };
  setSavedQueryData: React.Dispatch<
    React.SetStateAction<{
      name: string;
      description: string;
      sql_query_id: string;
    }>
  >;
}>({
  savedQueryData: {
    name: "",
    description: "",
    sql_query_id: "",
  },
  setSavedQueryData: () => {},
});
