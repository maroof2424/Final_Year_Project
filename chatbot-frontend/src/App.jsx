import React, { useState } from "react";

const App = () => {
  const [message, setMessage] = useState("");
  const [chatLog, setChatLog] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const userMessage = message.trim();
    if (!userMessage) return;

    setChatLog((prev) => [...prev, { type: "user", text: userMessage }]);
    setMessage("");

    const response = await fetch("http://127.0.0.1:8000/api/chat/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message: userMessage }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let botMessage = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      botMessage += chunk;

      setChatLog((prev) => {
        const updated = [...prev];
        if (updated.length && updated[updated.length - 1].type === "bot") {
          updated[updated.length - 1].text += chunk;
        } else {
          updated.push({ type: "bot", text: chunk });
        }
        return updated;
      });
    }
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "600px", margin: "auto" }}>
      <h2>🤖 Gemini Chatbot</h2>
      <div style={{ border: "1px solid #ccc", padding: "1rem", minHeight: "300px", marginBottom: "1rem" }}>
        {chatLog.map((msg, idx) => (
          <p key={idx}>
            <strong>{msg.type === "user" ? "You" : "Gemini"}:</strong> {msg.text}
          </p>
        ))}
      </div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask something..."
          style={{ padding: "0.5rem", width: "80%" }}
        />
        <button type="submit" style={{ padding: "0.5rem" }}>Send</button>
      </form>
    </div>
  );
};

export default App;
