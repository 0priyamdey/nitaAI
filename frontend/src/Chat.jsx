// src/Chat.jsx
import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_URL = "http://localhost:8000/api/query";

export default function Chat() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]); // { id, text, sender: 'user'|'bot', source?, time }
    const [isLoading, setIsLoading] = useState(false);
    const listRef = useRef(null);
    const inputRef = useRef(null);

    useEffect(() => {
        if (!listRef.current) return;
        listRef.current.scrollTop = listRef.current.scrollHeight;
    }, [messages, isLoading]);

    const makeMsg = (text, sender, source = "") => ({
        id: Date.now() + Math.random(),
        text,
        sender,
        source,
        time: new Date().toISOString(),
    });

    const handleSubmit = async (e) => {
        e?.preventDefault();
        const trimmed = input.trim();
        if (!trimmed) return;

        const userMsg = makeMsg(trimmed, "user");
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            const { data } = await axios.post(API_URL, { query: trimmed });
            const botText = data?.answer ?? "No answer available.";
            const botSource = data?.source ?? "";
            const botMsg = makeMsg(botText, "bot", botSource);
            setMessages((prev) => [...prev, botMsg]);
        } catch (err) {
            console.error("API error", err);
            const errMsg = makeMsg(
                "Sorry — I'm having trouble connecting to the server. Please try again.",
                "bot"
            );
            setMessages((prev) => [...prev, errMsg]);
        } finally {
            setIsLoading(false);
            inputRef.current?.focus();
        }
    };

    return (
        <div className="flex flex-col h-screen bg-linear-to-b from-gray-50 to-gray-100 text-gray-800">
            <header className="flex-none bg-white/60 backdrop-blur-sm border-b border-gray-200">
                <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-lg bg-linear-to-tr from-indigo-600 to-sky-500 shadow-md flex items-center justify-center text-white font-bold">
                            AI
                        </div>
                        <div>
                            <h1 className="text-lg font-semibold">NITai — NIT Agartala AI Assistant</h1>
                            <p className="text-xs text-gray-500">Ask about courses, exams, notices and more</p>
                        </div>
                    </div>
                    <div className="text-xs text-gray-500 hidden sm:block">Professional · Fast · Reliable</div>
                </div>
            </header>

            <main className="flex-1 overflow-hidden">
                <div className="max-w-4xl mx-auto h-full flex flex-col">
                    <div
                        ref={listRef}
                        className="flex-1 overflow-y-auto px-6 py-6 space-y-4"
                        role="log"
                        aria-live="polite"
                    >
                        {messages.length === 0 && !isLoading && (
                            <div className="mt-12 text-center text-gray-500">
                                <div className="text-4xl mb-4">💬</div>
                                <div>Welcome to NITai — ask a question about courses, exams or notices.</div>
                            </div>
                        )}

                        {messages.map((msg) => (
                            <div key={msg.id} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                                <div
                                    className={`max-w-[80%] sm:max-w-[60%] p-4 rounded-2xl shadow ${msg.sender === "user"
                                        ? "bg-indigo-600 text-white rounded-br-none"
                                        : "bg-white text-gray-800 rounded-bl-none"
                                        }`}
                                >
                                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.text}</div>

                                    <div className="mt-2 flex items-center justify-between text-[11px] opacity-75">
                                        <div className="italic">{msg.sender === "user" ? "You" : "NITai"}</div>
                                        <div className="text-right">
                                            {msg.sender === "bot" && msg.source && msg.source !== "No source found" && (
                                                <div className="text-xs text-gray-400">Source: {msg.source}</div>
                                            )}
                                            <div className="text-xs text-gray-400">
                                                {new Date(msg.time).toLocaleTimeString([], {
                                                    hour: "2-digit",
                                                    minute: "2-digit",
                                                })}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}

                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="p-3 rounded-2xl bg-white shadow text-sm text-gray-600">NITai is thinking…</div>
                            </div>
                        )}
                    </div>

                    <form onSubmit={handleSubmit} className="bg-white/70 border-t border-gray-200 p-4 shadow-inner" aria-label="Send a message">
                        <div className="max-w-4xl mx-auto flex items-center gap-3">
                            <input
                                ref={inputRef}
                                type="text"
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                placeholder="Ask about courses, exams, or notices..."
                                disabled={isLoading}
                                className="flex-1 min-h-11 px-4 py-2 bg-white border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-400 placeholder:text-gray-400"
                                aria-label="Chat input"
                            />

                            <button
                                type="submit"
                                disabled={isLoading || !input.trim()}
                                className="inline-flex items-center gap-3 px-5 py-2 rounded-full bg-linear-to-r from-indigo-600 to-sky-500 text-white font-semibold shadow-md hover:opacity-95 active:scale-95 disabled:opacity-60 transition"
                                aria-label="Send message"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 -rotate-45" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M22 2L11 13" />
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M22 2l-7 20-4-9-9-4 20-7z" />
                                </svg>
                                <span className="text-sm">Send</span>
                            </button>
                        </div>
                    </form>
                </div>
            </main>
        </div>
    );
}
