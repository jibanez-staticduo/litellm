"use client";

import { useCallback, useEffect, useRef, type Dispatch, type SetStateAction } from "react";
import { getMCPLoopbackOAuthStatus, markMCPLoopbackTunnelReady, startMCPLoopbackOAuth } from "@/components/networking";
import { toast } from "@/lib/toast";
import { extractErrorMessage } from "@/utils/errorUtils";
import type { UserMcpOAuthStatus } from "./useUserMcpOAuthFlow";

const LOOPBACK_POLL_INTERVAL_MS = 2000;
const LOOPBACK_TIMEOUT_MS = 300000;

interface LoopbackFlowOptions {
  accessToken: string;
  serverId: string;
  onSuccess: () => void;
  setStatus: Dispatch<SetStateAction<UserMcpOAuthStatus>>;
  setError: Dispatch<SetStateAction<string | null>>;
}

export const useLoopbackMcpOAuthFlow = ({
  accessToken,
  serverId,
  onSuccess,
  setStatus,
  setError,
}: LoopbackFlowOptions) => {
  const loopbackAbortRef = useRef<AbortController | null>(null);
  const loopbackWindowRef = useRef<Window | null>(null);

  const cancelLoopbackOAuthFlow = useCallback(() => {
    loopbackAbortRef.current?.abort();
    loopbackAbortRef.current = null;
    loopbackWindowRef.current?.close();
    loopbackWindowRef.current = null;
    setError(null);
    setStatus("cancelled");
  }, [setError, setStatus]);

  const startLoopbackOAuthFlow = useCallback(async () => {
    if (!accessToken) {
      setError("Sign in before connecting Lovable.");
      setStatus("error");
      return;
    }
    const popup = window.open(
      "about:blank",
      `litellm-lovable-oauth-${crypto.randomUUID()}`,
      "popup=yes,width=720,height=760",
    );
    if (!popup) {
      setError("Allow pop-ups for this site, then try again.");
      setStatus("error");
      return;
    }
    const abortController = new AbortController();
    loopbackAbortRef.current = abortController;
    loopbackWindowRef.current = popup;
    setStatus("authorizing");
    setError(null);
    try {
      const start = await startMCPLoopbackOAuth(accessToken, serverId);
      if (abortController.signal.aborted) return;
      setStatus("preflighting");
      try {
        await markMCPLoopbackTunnelReady(start.transaction_id, abortController.signal);
        const readiness = await getMCPLoopbackOAuthStatus(accessToken, serverId, start.transaction_id);
        if (readiness.status !== "ready") throw new Error("Tunnel readiness was not confirmed");
      } catch {
        if (abortController.signal.aborted) return;
        popup.close();
        loopbackWindowRef.current = null;
        const message =
          "Tunnel unavailable. Start the macOS SSH tunnel, verify http://127.0.0.1:43119/healthz, then retry.";
        setError(message);
        setStatus("error");
        toast.error(message);
        return;
      }
      if (abortController.signal.aborted) return;
      popup.location.replace(start.authorization_url);
      setStatus("waiting");
      const deadline = Date.now() + Math.min(start.expires_in * 1000, LOOPBACK_TIMEOUT_MS);
      while (!abortController.signal.aborted && Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, LOOPBACK_POLL_INTERVAL_MS));
        if (abortController.signal.aborted) return;
        if (popup.closed) throw new Error("Connection window closed before Lovable was connected.");
        const transaction = await getMCPLoopbackOAuthStatus(accessToken, serverId, start.transaction_id);
        if (transaction.status === "connected") {
          popup.close();
          loopbackWindowRef.current = null;
          setStatus("success");
          toast.success("Connected successfully");
          onSuccess();
          return;
        }
        if (transaction.status === "denied") throw new Error("Lovable connection was not approved.");
        if (transaction.status === "failed") throw new Error("Lovable connection failed. Start a new connection.");
      }
      if (!abortController.signal.aborted) throw new Error("Connection timed out. Start a new connection to retry.");
    } catch (err) {
      if (abortController.signal.aborted) return;
      popup.close();
      loopbackWindowRef.current = null;
      const message = extractErrorMessage(err);
      setError(message);
      setStatus("error");
      toast.error(message);
    } finally {
      if (loopbackAbortRef.current === abortController) loopbackAbortRef.current = null;
    }
  }, [accessToken, onSuccess, serverId, setError, setStatus]);

  useEffect(
    () => () => {
      loopbackAbortRef.current?.abort();
      loopbackWindowRef.current?.close();
    },
    [],
  );

  return { startLoopbackOAuthFlow, cancelLoopbackOAuthFlow };
};
