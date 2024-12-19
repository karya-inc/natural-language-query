function useChat({ input, id }: { input: string; id: string }) {
  async function postChat(url: string) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify({
        query: input,
        session_id: id,
      }),
    });

    const reader = response.body?.getReader();
    return reader;
  }

  async function getTableData(url: string) {
    const response = await fetch(url, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });

    return response.json();
  }

  return { postChat, getTableData };
}

export default useChat;
