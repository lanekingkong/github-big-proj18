# UAMP Plugin Development Guide

## Overview

UAMP plugins extend the platform to support any AI tool. Plugins are standalone JavaScript modules that implement a standardized interface.

## Plugin Structure

```
my-plugin/
├── manifest.json    # Plugin metadata and configuration
├── index.js         # Plugin entry point
└── README.md        # Plugin documentation
```

## Manifest Format

```json
{
  "name": "uamp-plugin-my-tool",
  "version": "1.0.0",
  "tool": "my-ai-tool",
  "description": "UAMP plugin for My AI Tool",
  "author": "Your Name",
  "license": "MIT",
  "entryPoint": "index.js",
  "capabilities": [
    "context_extraction",
    "context_application",
    "auto_sync"
  ],
  "configSchema": {
    "auto_sync": {
      "type": "boolean",
      "default": true,
      "description": "Automatically sync context"
    }
  }
}
```

## Plugin Interface

Every plugin must export a class that implements:

```javascript
class MyPlugin {
  /**
   * Initialize the plugin with optional config
   */
  async initialize(config = {}) {}

  /**
   * Extract context from the AI tool
   * @returns {Promise<Context>}
   */
  async extractContext() {}

  /**
   * Apply context to the AI tool
   * @param {Context} context
   */
  async applyContext(context) {}

  /**
   * Get plugin capabilities
   * @returns {string[]}
   */
  getCapabilities() {}

  /**
   * Clean up resources
   */
  async destroy() {}
}
```

## Context Object

```javascript
{
  id: "uuid",           // Unique context ID
  tool: "my-ai-tool",   // Tool identifier
  content: "string",    // Extracted context content
  metadata: {
    project: "string",  // Current project name
    file: "string",     // Current file path
    timestamp: 123,     // Unix timestamp (ms)
    tags: ["tag1"],     // Auto-generated tags
    importance: 75      // 0-100 importance score
  },
  relationships: {
    parents: [],        // Parent context IDs
    children: [],       // Child context IDs
    references: []      // Referenced context IDs
  }
}
```

## UAMP Client Library

Plugins can use the built-in UAMP client:

```javascript
const { UAMPClient } = require('./uamp-client');

class MyPlugin {
  constructor() {
    this.client = new UAMPClient({
      serverUrl: 'http://localhost:8080',
      wsUrl: 'ws://localhost:8081'
    });
  }

  async initialize() {
    await this.client.connect();
  }

  async syncContext(context) {
    await this.client.pushContext(context);
  }

  async getRelatedContext(query) {
    return await this.client.searchContext(query, this.tool);
  }
}
```

## Testing Your Plugin

1. Install UAMP server: `npm install -g uamp`
2. Start the server: `uamp start`
3. Copy plugin to plugins directory: `cp -r my-plugin ~/.uamp/plugins/`
4. Verify plugin is loaded: `curl http://localhost:8080/api/v1/plugins`

## Publishing

1. Create a GitHub repository: `uamp-plugin-{tool-name}`
2. Tag your release: `git tag v1.0.0`
3. Submit to UAMP Plugin Registry (coming soon)

## Best Practices

- Always use UUID v4 for context IDs
- Include project context in extractions
- Implement exponential backoff for reconnections
- Log errors with timestamps
- Support both auto and manual sync modes
- Test with multiple simultaneous connections
- Handle rate limiting gracefully
- Clean up resources in destroy()