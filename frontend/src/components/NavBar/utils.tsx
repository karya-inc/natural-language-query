import { createContext } from "react";

export interface SavedQueryDataInterface {
  sql_query_id: string;
  name: string;
  description: string;
}

export const SavedQueryContext = createContext<{
  setSavedQueries: React.Dispatch<
    React.SetStateAction<SavedQueryDataInterface[]>
  >;
}>({
  setSavedQueries: () => {},
});
