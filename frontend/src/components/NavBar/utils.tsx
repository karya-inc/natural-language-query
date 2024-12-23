import { createContext } from "react";

export const SavedQueryContext = createContext<{
  savedQueryData: {
    title: string;
    description: string;
    sql_query_id: string;
  };
  setSavedQueryData: React.Dispatch<
    React.SetStateAction<{
      title: string;
      description: string;
      sql_query_id: string;
    }>
  >;
}>({
  savedQueryData: {
    title: "",
    description: "",
    sql_query_id: "",
  },
  setSavedQueryData: () => {},
});
