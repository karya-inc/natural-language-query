import { useState } from "react";

interface HistoryItem {
  session_id: string;
  nlq: string;
}

const useNavBar = (title?: string, description?: string) => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [savedQueries, setSavedQueries] = useState<any[]>([]);
  async function getHistory(url: string) {
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

  async function getSavedQueries(url: string) {
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
    } catch (error) {
      console.error(error);
    }
  }

  async function postSavedQuery(url: string) {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ name: title, description }),
      });
      const data = await response.json();
      console.log(data);

      setSavedQueries((prev) => [data, ...prev]);
      console.log(data);
    } catch (error) {
      console.error(error);
    }
  }

  return {
    history,
    setHistory,
    getHistory,
    savedQueries,
    getSavedQueries,
    postSavedQuery,
  };
};

export default useNavBar;
