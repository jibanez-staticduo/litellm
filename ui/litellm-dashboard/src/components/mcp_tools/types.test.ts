import { describe, expect, it } from "vitest";
import { AUTH_TYPE, isLovableLoopbackOAuthServer, LOVABLE_LOOPBACK_SERVER_ID } from "./types";

const reviewed = {
  server_id: LOVABLE_LOOPBACK_SERVER_ID,
  url: "https://mcp.lovable.dev",
  auth_type: AUTH_TYPE.OAUTH2,
  oauth2_flow: "authorization_code",
  issuer: "https://lovable.dev/oauth",
  authorization_url: "https://lovable.dev/oauth/authorize",
  token_url: "https://lovable.dev/oauth/token",
  registration_url: "https://lovable.dev/oauth/register",
};

describe("isLovableLoopbackOAuthServer", () => {
  it("requires the immutable server id and verified provider metadata", () => {
    expect(isLovableLoopbackOAuthServer(reviewed)).toBe(true);
    expect(isLovableLoopbackOAuthServer({ ...reviewed, server_id: "other" })).toBe(false);
    expect(isLovableLoopbackOAuthServer({ ...reviewed, issuer: "https://other.example" })).toBe(false);
  });
});
