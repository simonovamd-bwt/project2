"use client";

import { useEffect, useRef, useState } from "react";
import { renderMarkdown } from "../lib/markdown";

/**
 * AI chat interface with live document preview (issue #2).
 *
 * Replaces the static form: the (mock) assistant opens the conversation, asks
 * one hard-coded question at a time, and the document preview on the right
 * updates live with every answer. When the interview completes, a Download PDF
 * button appears. No real LLM call — the backend /api/chat is a deterministic
 * stub, so this works with no API key.
 */
type ChatResponse = {
  reply: string;
  next_field: string | null;
  complete: boolean;
  fields: Record<string, string>;
  document_type: string;
  title: string;
  markdown: string;
  total_questions: number;
  answered: number;
};

type Message = { role: "ai" | "user"; text: string };

// Same-origin in the single container; overridable for split dev.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "";

async function postChat(answers: Record<string, string>): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
  if (!res.ok) throw new Error(`Chat request failed: ${res.status}`);
  return res.json();
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [turn, setTurn] = useState<ChatResponse | null>(null);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const logRef = useRef<HTMLDivElement>(null);

  // Kick off the conversation: the AI greets and asks the first question.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const first = await postChat({});
        if (cancelled) return;
        setTurn(first);
        setMessages([{ role: "ai", text: first.reply }]);
      } catch {
        if (!cancelled) setError("Не вдалося звʼязатися з асистентом.");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  // Keep the chat scrolled to the newest message.
  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight });
  }, [messages]);

  async function sendAnswer(e: React.FormEvent) {
    e.preventDefault();
    const value = input.trim();
    if (!value || busy || !turn || turn.complete || !turn.next_field) return;

    const nextAnswers = { ...answers, [turn.next_field]: value };
    setMessages((m) => [...m, { role: "user", text: value }]);
    setInput("");
    setAnswers(nextAnswers);
    setBusy(true);
    setError(null);

    try {
      const next = await postChat(nextAnswers);
      setTurn(next);
      setMessages((m) => [...m, { role: "ai", text: next.reply }]);
    } catch {
      setError("Помилка відповіді асистента. Спробуйте ще раз.");
    } finally {
      setBusy(false);
    }
  }

  const complete = turn?.complete ?? false;
  const answered = turn?.answered ?? 0;
  const total = turn?.total_questions ?? 4;
  const previewMarkdown = turn?.markdown ?? "";

  return (
    <div className="chat-layout print-root">
      {/* Chat panel */}
      <div className="chat-panel">
        <div className="chat-panel__header">
          <h2 className="chat-panel__title">Асистент з угод</h2>
          <span className="chat-progress">
            {answered} / {total}
          </span>
        </div>

        <div className="chat-log" ref={logRef}>
          {messages.map((m, i) => (
            <div key={i} className={`msg msg--${m.role}`}>
              {m.text}
            </div>
          ))}
          {error && <div className="msg msg--ai save-status--error">{error}</div>}
        </div>

        <form className="chat-input" onSubmit={sendAnswer}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={complete ? "Діалог завершено" : "Ваша відповідь…"}
            disabled={busy || complete}
            aria-label="Ваша відповідь"
            autoFocus
          />
          <button type="submit" className="btn" disabled={busy || complete}>
            {busy ? "…" : "Надіслати"}
          </button>
        </form>
      </div>

      {/* Live preview panel */}
      <div className="preview-panel">
        <div className="preview-panel__header">
          <h2 className="preview-panel__title">Прев’ю документа</h2>
          {complete && (
            <button
              type="button"
              className="btn"
              onClick={() => window.print()}
            >
              Download PDF
            </button>
          )}
        </div>
        <div className="preview-body">
          <div
            className="preview-doc"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(previewMarkdown) }}
          />
        </div>
      </div>
    </div>
  );
}
