#!/usr/bin/env node

/**
 * Cursor Hooks Langfuse Integration
 * 
 * Main entry point for Cursor hooks that sends traces to Langfuse.
 * 
 * Features:
 * - All 12 Cursor hooks supported (Agent + Tab)
 * - Traces grouped by conversation_id
 * - Sessions grouped by workspace
 * - Dynamic tags based on activity
 * - Completion scores and efficiency metrics
 * - Rich metadata and edit statistics
 * 
 * @version 1.1.0
 * @see https://cursor.com/docs/agent/hooks
 * @see https://langfuse.com/docs
 */

import { readStdin } from './lib/utils.js';
import { 
  getOrCreateTrace, 
  flushLangfuse,
  HOOK_HANDLER_VERSION,
} from './lib/langfuse-client.js';
import { routeHookHandler } from './lib/handlers.js';

/**
 * Main handler function
 * Reads hook data from stdin, creates Langfuse trace, and routes to handler
 */
async function main() {
  try {
    // Read JSON input from stdin
    const input = await readStdin();
    
    // Get or create a trace for this conversation
    const trace = getOrCreateTrace(input);
    
    // Route to the appropriate handler based on hook type
    const hookName = input.hook_event_name;
    const response = routeHookHandler(hookName, trace, input);
    
    // Output response to Cursor if handler returned one
    if (response !== null && response !== undefined) {
      console.log(JSON.stringify(response));
    }
    
    // Flush all pending events to Langfuse before exiting
    await flushLangfuse();
    
  } catch (error) {
    // Log error but don't crash - we don't want to block Cursor
    console.error(`[Langfuse Hook v${HOOK_HANDLER_VERSION}] Error: ${error.message}`);
    
    // Still output a permissive response so Cursor can continue
    // This ensures the hook doesn't block operations if something goes wrong
    console.log(JSON.stringify({ 
      continue: true, 
      permission: 'allow' 
    }));
    
    process.exit(1);
  }
}

// Run the main function
main();
