import React, { useState, useEffect } from "react";
import useWebSocket from "react-use-websocket";

export default function KafkaConsumerComponent() {
  const [messages, setMessages] = useState([]);

  // const { lastMessage, lastJsonMessage, readyState } = useWebSocket("ws://localhost:8089/ws/scenes");
  // const obj = useWebSocket("ws://localhost:8089/ws/scenes");
  // console.log(lastJsonMessage)

  const socket = new WebSocket("ws://localhost:8089/ws/scenes", + "mytoken" );
  console.log(socket)

  // useEffect(() => {
  //   console.log(lastMessage, readyState)
  //   if (lastMessage !== null) {
  //     setMessages((prev) => prev.concat(JSON.parse(lastMessage.data)));
  //   }
  // }, [lastMessage]);

  return (
    <div className="relative">
      <p>The WebSocket is currently {socket.readyState} </p>
      {messages.map((msg, idx) => (
        <span key={idx}>{msg}, </span>
      ))}
    </div>
  );
}
