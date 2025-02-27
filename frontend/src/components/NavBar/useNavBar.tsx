import { useState } from "react";
import { useParams } from "react-router-dom";
import { BACKEND_URL } from "../../config";

interface HistoryItem {
  session_id: string;
  nlq: string;
}

export interface SavedQueryDataInterface {
  sql_query_id: string;
  name: string;
  description: string;
}

export type ExecutionLog = {
  status: string;
  id: string;
  query_id: string;
  query: string;
  logs?: Record<string, unknown>[];
  created_at: string;
  completed_at: string;
};

export type ExecutionResponse = {
  execution_log: ExecutionLog;
  result?: Record<string, unknown>[];
  column_order?: string[];
};

const useNavBar = (name?: string, description?: string) => {
  const [navOpen, setNavOpen] = useState(true);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [savedQueries, setSavedQueries] = useState<SavedQueryDataInterface[]>(
    [],
  );
  const { savedId } = useParams();
  const [savedQueryData, setSavedQueryData] = useState({
    sql_query_id: "",
    name: "",
    description: "",
  });
  const [savedQueryTableData, setSavedQueryTableData] = useState<
    Record<string, unknown>[]
  >([]);

  async function getAllHistory(url: string) {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error(error);
    }
  }

  async function getAllSavedQueries(url: string) {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const data = await response.json();
      setSavedQueries(data);
      if (savedId) {
        setSavedQueryData(
          data.find(
            (query: SavedQueryDataInterface) => query.sql_query_id === savedId,
          ),
        );
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function saveQuery(url: string) {
    try {
      await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ name, description }),
      });
      await getAllSavedQueries(`${BACKEND_URL}/queries`);
    } catch (error) {
      console.error(error);
    }
  }

  async function executeSavedQueryByQueryId(
    url: string,
  ): Promise<ExecutionLog | undefined> {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      return await response.json();
    } catch (error) {
      console.error(error);
    }
  }

  async function getExecutionResponseById(
    url: string,
  ): Promise<ExecutionResponse | undefined> {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error(error);
    }
  }

  return {
    history,
    setHistory,
    getAllHistory,
    savedQueries,
    getAllSavedQueries,
    saveQuery,
    navOpen,
    setNavOpen,
    savedQueryData,
    setSavedQueryData,
    getExecutionResponseById,
    executeSavedQueryByQueryId,
    savedQueryTableData,
    setSavedQueryTableData,
    savedId,
    setSavedQueries,
  };
};

export default useNavBar;
