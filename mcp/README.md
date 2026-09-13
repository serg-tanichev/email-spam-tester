# Email Spam Tester over MCP

The service exposes an MCP server at `https://email-spam-tester.com/mcp` over streamable HTTP. No key, no account. Four tools:

| Tool | What it does |
|---|---|
| `get_test_address(lang="en")` | Reserves a disposable address and returns it with the slug and the report URL. `lang` decides the language of the fix plan a person sees on the report page. |
| `wait_for_report(slug, timeout_seconds=150)` | Blocks until the analysis is done and returns a summary: scores, the failing and warning checks with their evidence, the fix plan. Nothing to poll and no sleep loop to get wrong. |
| `get_report(slug)` | Reads an existing report without waiting. |
| `get_message_source(slug)` | The message as delivered: headers in wire order, both bodies, the raw source. |

The agent's job in between is to send a real message to the address, from the platform that will send the campaign. Half the checks read headers the sending platform adds, so a copy sent from a laptop says little about it.

## Claude Desktop

Add the server to `claude_desktop_config.json` (see [claude-desktop.json](claude-desktop.json) for the whole file):

```json
{
  "mcpServers": {
    "email-spam-tester": {
      "url": "https://email-spam-tester.com/mcp"
    }
  }
}
```

Clients that do not speak streamable HTTP directly can bridge it with `mcp-remote`:

```json
{
  "mcpServers": {
    "email-spam-tester": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://email-spam-tester.com/mcp"]
    }
  }
}
```

## Claude Code

```bash
claude mcp add --transport http email-spam-tester https://email-spam-tester.com/mcp
```

## Reading what comes back

- The per-check lines the tools return are in English whatever `lang` was set to; `lang` decides what the person opening the report URL sees.
- A check status of `skip` is not a pass: the check did not apply. `error` means it could not run and is left out of the score.
- `complete: false` means something could not be checked. Treat the score as optimistic until it is true.
- The slug is the capability: whoever holds it can read the report, including the subject, the sender, the bounce address and the full source. Do not test somebody else's mail without asking.

The same instructions, written for an agent to read before it starts, are in [SKILL.md](../SKILL.md).
