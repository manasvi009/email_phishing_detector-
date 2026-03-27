import axios from "axios";
import { demoPhishingResult, demoSafeResult, scanHistory } from "../data/mockData";

export const apiClient = axios.create({
  baseURL: "/api",
  timeout: 2500,
});

const suspiciousTokens = [
  "urgent",
  "verify",
  "suspended",
  "reset",
  "click here",
  "confirm",
  "invoice",
  "password",
  "security alert",
];

export async function analyzeEmail(payload) {
  await new Promise((resolve) => setTimeout(resolve, 1500));
  const combined = `${payload.subject || ""} ${payload.sender || ""} ${payload.content || ""} ${payload.url || ""}`.toLowerCase();
  const isPhishing = suspiciousTokens.some((token) => combined.includes(token));
  return {
    ...(isPhishing ? demoPhishingResult : demoSafeResult),
    sender: payload.sender || "unknown@domain.com",
    subject: payload.subject || "Untitled email",
    analyzedAt: new Date().toISOString(),
  };
}

export async function fetchHistory() {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return scanHistory;
}
