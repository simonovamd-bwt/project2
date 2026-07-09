"use client";

import { useState } from "react";
import BrandHeader from "./BrandHeader";

type Mode = "login" | "register";

/**
 * Auth screen (issue #8): a Sign In / Sign Up card whose copy swaps with the
 * mode, matching the reference's renderAuthMode() behaviour. This PR is the
 * visual foundation — submitting shows an inline status placeholder rather
 * than calling the API (wiring to /api/auth is issue #2's scope).
 */
const COPY: Record<Mode, { title: string; subtitle: string; cta: string }> = {
  login: {
    title: "Welcome back",
    subtitle: "Увійдіть, щоб побачити свою історію документів.",
    cta: "Sign in",
  },
  register: {
    title: "Create your account",
    subtitle: "Зареєструйтесь, щоб зберігати згенеровані документи.",
    cta: "Sign up",
  },
};

export default function AuthCard() {
  const [mode, setMode] = useState<Mode>("login");
  const [status, setStatus] = useState<string | null>(null);
  const copy = COPY[mode];

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // Visual foundation only — real auth wiring lands with the chat UI (#2).
    setStatus("Демо-режим: підключення до бекенду з’явиться в Issue #2.");
  }

  function switchMode(next: Mode) {
    setMode(next);
    setStatus(null);
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <BrandHeader compact />
        <h1 className="auth-title">{copy.title}</h1>
        <p className="auth-subtitle">{copy.subtitle}</p>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Імʼя користувача</label>
            <input id="username" name="username" type="text" autoComplete="username" />
          </div>
          <div className="field">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete={mode === "login" ? "current-password" : "new-password"}
            />
          </div>
          <button type="submit" className="btn btn--block">
            {copy.cta}
          </button>
        </form>

        {status && <div className="save-status">{status}</div>}

        <p className="auth-switch">
          {mode === "login" ? (
            <>
              Ще немає акаунту?{" "}
              <button type="button" onClick={() => switchMode("register")}>
                Sign up
              </button>
            </>
          ) : (
            <>
              Вже маєте акаунт?{" "}
              <button type="button" onClick={() => switchMode("login")}>
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
