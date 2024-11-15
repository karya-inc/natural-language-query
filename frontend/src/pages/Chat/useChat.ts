function useChat({ input, sessionId }: { input: string; sessionId: string }) {
  async function postChat(url: string) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        query: input,
        session_id: sessionId,
      }),
    });

    const reader = response.body?.getReader();
    return reader;
  }
  return { postChat };
}

export default useChat;
