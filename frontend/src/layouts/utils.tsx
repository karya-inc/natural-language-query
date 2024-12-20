import { useEffect, useState } from "react";
import { Message } from "../pages/Chat";
import { BACKEND_URL } from "../config";
import { useParams } from "react-router-dom";

const useChatHistory = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { sessionHistoryId, savedId } = useParams();
  const [id, setId] = useState(sessionHistoryId ?? savedId);
  const [conversationStarted, setConversationStarted] = useState(false);

  useEffect(() => {
    if (sessionHistoryId) {
      setConversationStarted(true);
      getChatHistory(
        `${BACKEND_URL}/fetch_session_history/${sessionHistoryId}`
      );
    }
    if (savedId) {
      setConversationStarted(true);
    }
  }, [id]);

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

  return {
    messages,
    conversationStarted,
    setConversationStarted,
    setMessages,
    getChatHistory,
    id,
    setId,
  };
};

export default useChatHistory;
