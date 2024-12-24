import { useState } from "react";
import { useParams } from "react-router-dom";

interface HistoryItem {
  session_id: string;
  nlq: string;
}

export interface SavedQueryDataInterface {
  sql_query_id: string;
  name: string;
  description: string;
}

const useNavBar = (name?: string, description?: string) => {
  const [navOpen, setNavOpen] = useState(true);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [savedQueries, setSavedQueries] = useState<SavedQueryDataInterface[]>(
    []
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
      setSavedQueryData(
        data.find(
          (query: SavedQueryDataInterface) => query.sql_query_id === savedId
        )
      );
    } catch (error) {
      console.error(error);
    }
  }

  async function saveQuery(url: string) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ name, description }),
      });
      const data = await response.json();
      setSavedQueries((prev) => [data, ...prev]);
    } catch (error) {
      console.error(error);
    }
  }

  async function postQueryToGetId(url: string) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const { id } = await response.json();
      return id;
    } catch (error) {
      console.error(error);
    }
  }

  async function getSavedQueryTableData(url: string) {
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
    getSavedQueryTableData,
    postQueryToGetId,
    savedQueryTableData,
    setSavedQueryTableData,
    savedId,
  };
};

export default useNavBar;
