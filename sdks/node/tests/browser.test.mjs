import test from "node:test";
import assert from "node:assert";
import { cdpLaunchArgs } from "../dist/browser.js";

test("CDP launch args include automation and remote debugging flags", () => {
  const args = cdpLaunchArgs(true);
  assert.ok(args.includes("--remote-debugging-port=0"));
  assert.ok(args.includes("--remote-allow-origins=*"));
  assert.ok(args.includes("--shardx-automation"));
});

test("non-CDP launch args omit automation and remote debugging flags", () => {
  assert.deepStrictEqual(cdpLaunchArgs(false), []);
});
