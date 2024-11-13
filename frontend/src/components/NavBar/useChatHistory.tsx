import { useState } from "react";
import historySessions from "../../data/history.json";

const useHistory = () => {
  const [history, setHistory] = useState(historySessions);
  async function getHistory(url: string) {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });
      const data = await response.json();
      setHistory(data);
    } catch (error) {
      console.error(error);
    }
  }

  return { history, getHistory };
};

export default useHistory;
