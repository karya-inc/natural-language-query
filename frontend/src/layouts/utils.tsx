import { useState } from "react";
import { Message } from "../pages/Chat";

const useChatHistory = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  async function getChatHistory(url: string) {
    try {
      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const data = await response.json();
      setMessages(data);
    } catch (error) {
      console.error(error);
    }
  }

  return { messages, setMessages, getChatHistory };
};

export default useChatHistory;
