#!/usr/bin/env node

const DEFAULT_BASE_URL = "https://diy.youzanyun.com";

function parseArgs(argv) {
  const options = {
    command: "",
    baseUrl: process.env.YOUZAN_OPEN_PLATFORM_BASE_URL || DEFAULT_BASE_URL,
    cookie: process.env.YOUZAN_OPEN_PLATFORM_COOKIE || "",
    referer: process.env.YOUZAN_OPEN_PLATFORM_REFERER || "",
    raw: false,
    params: { state: "", msgKey: "", apiKey: "", packageKey: "" },
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    const next = argv[index + 1];
    if (arg === "--help" || arg === "-h") options.help = true;
    else if (arg === "--raw") options.raw = true;
    else if (["--base-url", "--referer", "--state", "--msgKey", "--apiKey", "--packageKey"].includes(arg)) {
      if (!next || next.startsWith("-")) throw new Error(`${arg} requires a value`);
      if (arg === "--base-url") options.baseUrl = next;
      else if (arg === "--referer") options.referer = next;
      else options.params[arg.slice(2)] = next;
      index += 1;
    } else if (arg.startsWith("-")) throw new Error(`Unknown option: ${arg}`);
    else if (!options.command) options.command = arg;
    else throw new Error(`Unexpected argument: ${arg}`);
  }
  return options;
}

function usage() {
  return `Usage:
  node scripts/platform.mjs category-packs [--apiKey key]
  node scripts/platform.mjs abilities [--raw]

Environment:
  YOUZAN_OPEN_PLATFORM_COOKIE    Required Cookie from diy.youzanyun.com
  YOUZAN_OPEN_PLATFORM_BASE_URL  Optional, default ${DEFAULT_BASE_URL}`;
}

function normalizeCommand(command) {
  if (["category-packs", "categories", "category"].includes(command)) return "category-packs";
  if (["abilities", "api-abilities", "ability"].includes(command)) return "abilities";
  return command;
}

function buildRequest(options) {
  const command = normalizeCommand(options.command);
  const baseUrl = options.baseUrl.replace(/\/+$/, "");
  if (command === "category-packs") {
    const url = new URL(`${baseUrl}/api/apps/search-app-category-capability-pack`);
    for (const [key, value] of Object.entries(options.params)) url.searchParams.set(key, value);
    return { command, url, referer: options.referer || `${baseUrl}/application/category/package` };
  }
  if (command === "abilities") {
    return {
      command,
      url: new URL(`${baseUrl}/api/apps/get-all-ability`),
      referer: options.referer || `${baseUrl}/application/category/ability`,
    };
  }
  throw new Error(`Unknown command: ${options.command}`);
}

function summarize(value) {
  const data = value && typeof value === "object" && "data" in value ? value.data : value;
  if (Array.isArray(data)) return { dataShape: `array(${data.length})`, itemCount: data.length };
  if (!data || typeof data !== "object") return { dataShape: typeof data };
  return { dataShape: `object(${Object.keys(data).slice(0, 12).join(", ")})` };
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help || !options.command) {
    console.log(usage());
    return;
  }
  if (!options.cookie) throw new Error("Missing YOUZAN_OPEN_PLATFORM_COOKIE.");

  const request = buildRequest(options);
  const response = await fetch(request.url, {
    headers: {
      accept: "application/json, text/plain, */*",
      cookie: options.cookie,
      referer: request.referer,
      "user-agent": "Mozilla/5.0 YZY Toolkit",
    },
  });
  const text = await response.text();
  let body;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  if (!response.ok) throw new Error(`Open platform request failed: HTTP ${response.status}`);

  console.log(JSON.stringify(options.raw ? body : {
    command: request.command,
    request: { url: request.url.toString(), cookie: "<redacted>" },
    summary: summarize(body),
    raw: body,
  }, null, 2));
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
