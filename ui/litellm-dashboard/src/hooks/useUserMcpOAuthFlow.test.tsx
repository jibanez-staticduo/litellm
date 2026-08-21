import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as networking from "@/components/networking";
import NotificationsManager from "@/components/molecules/notifications_manager";
import { useUserMcpOAuthFlow } from "./useUserMcpOAuthFlow";

vi.mock("@/components/networking", () => ({
  buildMcpOAuthAuthorizeUrl: vi.fn(),
  exchangeMcpOAuthToken: vi.fn(),
  getMCPLoopbackOAuthStatus: vi.fn(),
  markMCPLoopbackTunnelReady: vi.fn(),
  registerMcpOAuthClient: vi.fn(),
  startMCPLoopbackOAuth: vi.fn(),
  storeMCPOAuthUserCredential: vi.fn(),
}));

vi.mock("@/components/molecules/notifications_manager", () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

const popup = {
  closed: false,
  close: vi.fn(),
  location: { replace: vi.fn() },
};

const renderFlow = (useLoopbackOAuth = true) =>
  renderHook(() =>
    useUserMcpOAuthFlow({
      accessToken: "user-session",
      serverId: "server-1",
      serverAlias: useLoopbackOAuth ? "Lovable display name" : "github",
      useLoopbackOAuth,
      onSuccess: vi.fn(),
    }),
  );

describe("useUserMcpOAuthFlow Lovable loopback routing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    popup.closed = false;
    vi.spyOn(window, "open").mockReturnValue(popup as unknown as Window);
  });

  it("reports a blocked popup before creating a transaction", async () => {
    vi.spyOn(window, "open").mockReturnValue(null);
    const { result } = renderFlow();

    await act(result.current.startOAuthFlow);

    expect(result.current.error).toContain("Allow pop-ups");
    expect(networking.startMCPLoopbackOAuth).not.toHaveBeenCalled();
  });

  it("does not navigate when browser LNA or loopback readiness fails", async () => {
    vi.mocked(networking.startMCPLoopbackOAuth).mockResolvedValue({
      authorization_url: "https://auth.example.test/authorize",
      transaction_id: "transaction-1",
      expires_in: 300,
    });
    vi.mocked(networking.markMCPLoopbackTunnelReady).mockRejectedValue(new TypeError("LNA denied"));
    const { result } = renderFlow();

    await act(result.current.startOAuthFlow);

    expect(networking.startMCPLoopbackOAuth).toHaveBeenCalled();
    expect(popup.location.replace).not.toHaveBeenCalled();
    expect(result.current.status).toBe("error");
    expect(result.current.error).toContain("Start the macOS SSH tunnel");
  });

  it("navigates only after backend-confirmed readiness and polls the exact transaction", async () => {
    vi.mocked(networking.markMCPLoopbackTunnelReady).mockResolvedValue();
    vi.mocked(networking.startMCPLoopbackOAuth).mockResolvedValue({
      authorization_url: "https://auth.example.test/authorize?opaque=1",
      transaction_id: "transaction-1",
      expires_in: 300,
    });
    vi.mocked(networking.getMCPLoopbackOAuthStatus)
      .mockResolvedValueOnce({ status: "ready" })
      .mockResolvedValueOnce({ status: "connected" });
    const { result } = renderFlow();

    await act(async () => {
      const completion = result.current.startOAuthFlow();
      await new Promise((resolve) => setTimeout(resolve, 2100));
      await completion;
    });

    expect(networking.markMCPLoopbackTunnelReady).toHaveBeenCalledWith("transaction-1", expect.any(AbortSignal));
    expect(networking.startMCPLoopbackOAuth).toHaveBeenCalledWith("user-session", "server-1");
    expect(popup.location.replace).toHaveBeenCalledWith("https://auth.example.test/authorize?opaque=1");
    expect(networking.getMCPLoopbackOAuthStatus).toHaveBeenLastCalledWith("user-session", "server-1", "transaction-1");
    expect(result.current.status).toBe("success");
    expect(NotificationsManager.success).toHaveBeenCalledWith("Connected successfully");
  }, 5000);

  it("keeps every non-Lovable server on the existing browser PKCE flow", async () => {
    vi.mocked(networking.registerMcpOAuthClient).mockResolvedValue({ client_id: "client-1" });
    vi.mocked(networking.buildMcpOAuthAuthorizeUrl).mockReturnValue("https://gateway.example.test/authorize");
    Object.defineProperty(window, "location", {
      value: { href: "https://app.example.test/ui" },
      configurable: true,
      writable: true,
    });
    const { result } = renderFlow(false);

    await act(result.current.startOAuthFlow);

    expect(networking.markMCPLoopbackTunnelReady).not.toHaveBeenCalled();
    expect(networking.startMCPLoopbackOAuth).not.toHaveBeenCalled();
    expect(networking.buildMcpOAuthAuthorizeUrl).toHaveBeenCalled();
    await waitFor(() => expect(window.location.href).toBe("https://gateway.example.test/authorize"));
  });

  it("cancels polling, closes the window, and does not report success", async () => {
    vi.mocked(networking.markMCPLoopbackTunnelReady).mockResolvedValue();
    vi.mocked(networking.startMCPLoopbackOAuth).mockResolvedValue({
      authorization_url: "https://auth.example.test/authorize",
      transaction_id: "transaction-1",
      expires_in: 300,
    });
    vi.mocked(networking.getMCPLoopbackOAuthStatus).mockResolvedValue({ status: "ready" });
    const { result } = renderFlow();

    act(() => {
      void result.current.startOAuthFlow();
    });
    await waitFor(() => expect(result.current.status).toBe("waiting"));
    act(() => {
      result.current.cancelOAuthFlow();
    });

    expect(result.current.status).toBe("cancelled");
    expect(popup.close).toHaveBeenCalled();
    expect(NotificationsManager.success).not.toHaveBeenCalled();
  });

  it("reports popup closure and transaction status errors", async () => {
    vi.mocked(networking.markMCPLoopbackTunnelReady).mockResolvedValue();
    vi.mocked(networking.startMCPLoopbackOAuth).mockResolvedValue({
      authorization_url: "https://auth.example.test/authorize",
      transaction_id: "transaction-1",
      expires_in: 300,
    });
    vi.mocked(networking.getMCPLoopbackOAuthStatus).mockResolvedValueOnce({ status: "ready" });
    popup.closed = true;
    const { result } = renderFlow();

    await act(async () => {
      const completion = result.current.startOAuthFlow();
      await new Promise((resolve) => setTimeout(resolve, 2100));
      await completion;
    });

    expect(result.current.status).toBe("error");
    expect(result.current.error).toContain("window closed");
  }, 5000);

  it("keeps concurrent hook instances on distinct popups and transaction status IDs", async () => {
    const openedNames: string[] = [];
    vi.spyOn(window, "open").mockImplementation((_url, name) => {
      openedNames.push(String(name));
      return { ...popup, closed: false, location: { replace: vi.fn() } } as unknown as Window;
    });
    vi.mocked(networking.markMCPLoopbackTunnelReady).mockResolvedValue();
    vi.mocked(networking.startMCPLoopbackOAuth)
      .mockResolvedValueOnce({
        authorization_url: "https://auth.example/one",
        transaction_id: "tx-one",
        expires_in: 300,
      })
      .mockResolvedValueOnce({
        authorization_url: "https://auth.example/two",
        transaction_id: "tx-two",
        expires_in: 300,
      });
    vi.mocked(networking.getMCPLoopbackOAuthStatus).mockImplementation(async (_token, _server, transactionId) => ({
      status: transactionId === "tx-one" || transactionId === "tx-two" ? "ready" : "failed",
    }));
    const first = renderFlow();
    const second = renderFlow();

    act(() => {
      void first.result.current.startOAuthFlow();
      void second.result.current.startOAuthFlow();
    });
    await waitFor(() => expect(first.result.current.status).toBe("waiting"));
    await waitFor(() => expect(second.result.current.status).toBe("waiting"));

    expect(new Set(openedNames).size).toBe(2);
    expect(networking.markMCPLoopbackTunnelReady).toHaveBeenCalledWith("tx-one", expect.any(AbortSignal));
    expect(networking.markMCPLoopbackTunnelReady).toHaveBeenCalledWith("tx-two", expect.any(AbortSignal));
    act(() => {
      first.result.current.cancelOAuthFlow();
      second.result.current.cancelOAuthFlow();
    });
  });
});
