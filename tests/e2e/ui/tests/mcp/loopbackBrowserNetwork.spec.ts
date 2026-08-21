import { expect, test } from "@playwright/test";
import { execFileSync } from "node:child_process";
import { createServer as createHttpServer } from "node:http";
import { createServer as createHttpsServer } from "node:https";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

test("HTTPS UI handles Chromium loopback LNA or mixed-content outcome", async ({ browser }) => {
  const directory = mkdtempSync(join(tmpdir(), "litellm-loopback-browser-"));
  const keyPath = join(directory, "key.pem");
  const certPath = join(directory, "cert.pem");
  execFileSync("openssl", [
    "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
    "-subj", "/CN=127.0.0.1", "-keyout", keyPath, "-out", certPath,
  ], { stdio: "ignore" });

  const relayRequests: string[] = [];
  const relay = createHttpServer((request, response) => {
    relayRequests.push(request.url ?? "");
    response.writeHead(200, { "Content-Type": "text/html", "Cache-Control": "no-store" });
    response.end("ready");
  });
  await new Promise<void>((resolve) => relay.listen(0, "127.0.0.1", resolve));
  const relayAddress = relay.address();
  if (!relayAddress || typeof relayAddress === "string") throw new Error("relay did not bind");

  const origin = createHttpsServer(
    { key: readFileSync(keyPath), cert: readFileSync(certPath) },
    (_request, response) => {
      response.writeHead(200, { "Content-Type": "text/html" });
      response.end(`<!doctype html><button id="connect">Connect</button><p id="status" role="alert"></p>
        <script>document.getElementById('connect').onclick=async()=>{const status=document.getElementById('status');const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),1000);try{await fetch('http://127.0.0.1:${relayAddress.port}/ready?transaction_id=${"t".repeat(43)}',{mode:'no-cors',credentials:'omit',cache:'no-store',referrerPolicy:'no-referrer',signal:controller.signal});status.textContent='ready-request-sent'}catch(e){status.textContent='Tunnel unavailable. Check browser local-network permission and the SSH tunnel.'}finally{clearTimeout(timeout)}}</script>`);
    },
  );
  await new Promise<void>((resolve) => origin.listen(0, "127.0.0.1", resolve));
  const originAddress = origin.address();
  if (!originAddress || typeof originAddress === "string") throw new Error("origin did not bind");

  try {
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    const page = await context.newPage();
    await page.goto(`https://127.0.0.1:${originAddress.port}`);
    await page.getByRole("button", { name: "Connect" }).click();
    const status = page.getByRole("alert");
    await expect(status).not.toBeEmpty();
    const message = await status.textContent();
    if (message === "ready-request-sent") {
      expect(relayRequests).toEqual([`/ready?transaction_id=${"t".repeat(43)}`]);
    } else {
      expect(message).toContain("Tunnel unavailable");
      expect(relayRequests).toEqual([]);
    }
    await context.close();
  } finally {
    await Promise.all([
      new Promise<void>((resolve) => relay.close(() => resolve())),
      new Promise<void>((resolve) => origin.close(() => resolve())),
    ]);
    rmSync(directory, { recursive: true, force: true });
  }
});
