#!/usr/bin/env python3
"""Zero-token streaming of the full raw transcript into Obsidian Central Brain."""

import json
from pathlib import Path

TRANSCRIPT_PATH = Path(r"C:\Users\arqam\.gemini\antigravity\brain\4e8d6f55-be3a-4a22-ae2c-35cbf6146aa3\.system_generated\logs\transcript_full.jsonl")
OUT_PATH = Path(r"D:\Comfy UI\idea memory\obsidian brains\big picture\99_Raw_Discussions\04_Navier_Stokes_3D\2026-11-20 - Raw Full Navier-Stokes Workspace Chat From Inception.md")


def stream_transcript():
    user_count = 0
    assistant_count = 0
    tool_call_count = 0
    tool_resp_count = 0
    total_steps = 0

    # First pass: count stats
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            total_steps += 1
            step = json.loads(line)
            stype = step.get("type", "")
            if stype == "USER_INPUT":
                user_count += 1
            elif stype == "PLANNER_RESPONSE":
                assistant_count += 1
                tool_call_count += len(step.get("tool_calls", []))
            elif stype == "TOOL_RESPONSE":
                tool_resp_count += 1

    print(f"Stats: {total_steps} steps ({user_count} user turns, {assistant_count} assistant responses, {tool_call_count} tool calls, {tool_resp_count} tool results)")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        out.write("# Raw Full Navier-Stokes (`tubulance`) Workspace Chat From Inception\n\n")
        out.write(f"**Conversation ID:** `4e8d6f55-be3a-4a22-ae2c-35cbf6146aa3`  \n")
        out.write(f"**Total Steps Streamed:** {total_steps} ({user_count} user turns, {assistant_count} assistant responses, {tool_call_count} tool calls, {tool_resp_count} tool results)  \n")
        out.write(f"**Companion Probe Window:** [[2026-11-20 - Raw Rosetta Cl30 Probe Window Chat (c013b63c)]]  \n")
        out.write(f"**Epistemic Lock:** `NS_GLOBAL_REGULARITY_OPEN: true` | `status: verified-finite`\n\n")
        out.write("---\n\n")

        with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                step = json.loads(line)
                idx = step.get("step_index", total_steps)
                stype = step.get("type", "")
                created = step.get("created_at", "")
                content = step.get("content", "")
                tool_calls = step.get("tool_calls", [])

                if stype == "USER_INPUT":
                    out.write(f"## [Step {idx}] USER ({created})\n\n")
                    out.write(f"{content}\n\n---\n\n")

                elif stype == "PLANNER_RESPONSE":
                    out.write(f"## [Step {idx}] ASSISTANT ({created})\n\n")
                    if content:
                        out.write(f"{content}\n\n")
                    if tool_calls:
                        out.write(f"### Tool Calls ({len(tool_calls)})\n\n")
                        for tc in tool_calls:
                            fn = tc.get("function", {}).get("name") or tc.get("name", "unknown")
                            args = tc.get("function", {}).get("arguments") or tc.get("args", {})
                            arg_summary = json.dumps(args, ensure_ascii=False)
                            if len(arg_summary) > 200:
                                arg_summary = arg_summary[:200] + "...}"
                            out.write(f"- **{fn}**: `{arg_summary}`\n")
                        out.write("\n")
                    out.write("---\n\n")

                elif stype == "TOOL_RESPONSE":
                    status = step.get("status", "DONE")
                    out.write(f"## [Step {idx}] TOOL RESPONSE ({status}, {created})\n\n")
                    c_str = str(content)
                    if len(c_str) > 1000:
                        c_str = c_str[:500] + f"\n... [truncated {len(c_str) - 1000} chars] ...\n" + c_str[-500:]
                    out.write(f"```\n{c_str}\n```\n\n---\n\n")

    print(f"Successfully streamed {total_steps} steps to {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    stream_transcript()
