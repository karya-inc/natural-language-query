import { Message } from "../pages/Chat";

function getData(session_id: string, user_query: string): Message[] {
  return [
    {
      id: 1,
      message: user_query,
      role: "user",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM sales",
    },
    {
      id: 2,
      message: "What would you like to search?",
      role: "bot",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM cars",
    },
    {
      id: 3,
      message: "I would like to search for ...",
      role: "user",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM bikes",
    },
    {
      id: 4,
      message: "Please be specific",
      role: "bot",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM operations",
    },
    {
      id: 5,
      message: "What is the highest sale for this month?",
      role: "user",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM computers",
    },
    {
      id: 6,
      message: "It was 100 thousand dollars",
      role: "bot",
      timestamp: Date.now(),
      session_id: session_id,
      kind: "TEXT",
      type: "text",
      query: "SELECT * FROM laptops",
    },
  ] as const;
}

export default getData;
