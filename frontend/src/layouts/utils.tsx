import { useContext, useEffect, useState } from "react";
import { Message } from "../pages/Chat";
import { BACKEND_URL } from "../config";
import { RouteContext } from "../App";
import { useParams } from "react-router-dom";

const useChatHistory = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { sessionHistoryId, savedId } = useParams();
  const [conversationStarted, setConversationStarted] = useState(false);
  const { sessionId, setSessionId, savedQueryId, setSavedQueryId } =
    useContext(RouteContext);

  useEffect(() => {
    if (sessionHistoryId) {
      setSessionId(sessionHistoryId);
      getChatHistory(
        `${BACKEND_URL}/fetch_session_history/${
          sessionId ? sessionId : sessionHistoryId
        }`
      );
      setConversationStarted(true);
    }
    if (savedId) {
      setSavedQueryId(savedId);
      getSavedQuery(
        `${BACKEND_URL}/fetch_session_history/${
          sessionId ? sessionId : sessionHistoryId
        }`
      );
      setConversationStarted(true);
    }
  }, [sessionId]);

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
  };
};

export default useChatHistory;
