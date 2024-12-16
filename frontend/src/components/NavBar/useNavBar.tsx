import { useState } from "react";

interface HistoryItem {
  session_id: string;
  nlq: string;
}

const useNavBar = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [savedQueries, setSavedQueries] = useState([]);
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

  return {
    history,
    setHistory,
    getHistory,
    savedQueries,
    getSavedQueries,
  };
};

export default useNavBar;
