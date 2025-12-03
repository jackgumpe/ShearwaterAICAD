# Root Router Fix - Exact Code Changes

## File: `src/core/routers/root_router.py`

### Change 1: Update AGENT_BRANCH_MAP (lines 33-42)

**OLD:**
```python
# --- Agent to Branch Mapping ---

# In a real dynamic system, this would be discovered automatically.

# For now, a static map is sufficient for our architecture.

AGENT_BRANCH_MAP = {

    "claude_code": "branch_core",

    "gemini_cli": "branch_core",

}
```

**NEW:**
```python
# --- Agent to Branch Mapping ---

# Maps agent names to their branch's DEALER identity (as bytes).
# Dynamic discovery: When a branch proxy sends a message for an agent,
# we learn that agent's location and cache it.

AGENT_BRANCH_MAP = {
    "claude_code": b"branch_core",
    "gemini_cli": b"branch_core",
}
```

**Why:** The map now stores BYTES (the actual DEALER identity), not strings. This is critical for ZMQ routing.

---

### Change 2: Fix Routing Logic (lines 96-125)

**OLD:**
```python
            # Look up the destination branch from our map

            dest_agent_str = destination_agent.decode()

            source_branch_str = proxy_identity.decode()

            # Try to get from map, or infer from sending branch as fallback
            dest_branch_identity = AGENT_BRANCH_MAP.get(dest_agent_str)



            if not dest_branch_identity:

                # Dynamic discovery: if the sending branch is trying to reach this agent,
                # assume the agent is on the same branch (same-branch routing)
                dest_branch_identity = source_branch_str
                logging.info(f"Learning: agent '{dest_agent_str}' is on branch '{dest_branch_identity}'")
                AGENT_BRANCH_MAP[dest_agent_str] = dest_branch_identity



            # Forward the message to the correct branch proxy.

            # The router uses the first frame as the address of the recipient proxy.

            # The proxy expects the remaining frames to be [destination_agent, original_sender, payload].

            router_socket.send_multipart([dest_branch_identity.encode(), destination_agent, original_sender, payload_str])



            logging.info(f"Relayed message for '{dest_agent_str}' to branch '{dest_branch_identity}'")
```

**NEW:**
```python
            # Look up the destination branch from our map

            dest_agent_str = destination_agent.decode()

            # Try to get from map - returns the branch's DEALER identity as stored
            dest_branch_identity_bytes = AGENT_BRANCH_MAP.get(dest_agent_str)



            if not dest_branch_identity_bytes:

                # Dynamic discovery: For same-branch routing, assume agent is on the same branch as sender.
                # Use proxy_identity directly since the sender knows how to reach this branch.
                dest_branch_identity_bytes = proxy_identity
                logging.info(f"Learning: agent '{dest_agent_str}' is on same branch as sender ('{proxy_identity.decode()}')")
                AGENT_BRANCH_MAP[dest_agent_str] = proxy_identity



            # Forward the message to the correct branch proxy.

            # The router uses the first frame as the address of the recipient proxy.

            # Use the branch's actual DEALER identity bytes for routing.

            router_socket.send_multipart([dest_branch_identity_bytes, destination_agent, original_sender, payload_str])



            logging.info(f"Relayed message for '{dest_agent_str}' to branch '{dest_branch_identity_bytes.decode()}'")
```

**Why:**
1. Store and use BYTES directly, not strings that get re-encoded
2. For unknown agents, use `proxy_identity` (the actual bytes sent from the proxy), not a re-encoded string
3. When ROUTER socket sends a message, the first frame MUST be the peer's identity as bytes - using the actual identity from the ROUTER's connection table, not a reconstructed string

---

## The Root Cause of Message Loss

When you use `dest_branch_identity.encode()`, you're creating a NEW bytes object. ZMQ ROUTER sockets don't recognize this as a valid identity because:

1. The proxy connected with identity `b"branch_core"` (created by the DEALER socket's setsockopt)
2. The ROUTER maintains an internal routing table with that exact byte sequence
3. When you `.encode()` a string, even if it's identical, it creates a different bytes object
4. ZMQ compares by identity/reference, not just content
5. Message to unrecognized identity = silent drop

**Solution:** Use `proxy_identity` directly (the bytes that arrived in the first frame of the received multipart message). This is GUARANTEED to be a valid routing identifier.

---

## Testing After Fix

1. Restart root_router.py (with this fix)
2. Restart branch_proxy.py
3. Run test agents or claude_client + gemini_cli
4. Check logs for "Learning:" message showing dynamic discovery working
5. Verify messages route successfully end-to-end
