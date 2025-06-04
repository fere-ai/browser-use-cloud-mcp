"""CLI entry point for the Browser Use Cloud MCP Server."""

import argparse
import asyncio
import logging
import sys
from typing import Optional

from mcp.server.models import InitializationOptions

from .server import app

logger = logging.getLogger(__name__)


async def run_stdio():
    """Run the server with stdio transport."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-use-cloud-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


async def run_http(host: str = "localhost", port: int = 8000):
    """Run the server with HTTP transport."""
    try:
        from mcp.server.fastapi import FastAPIServer

        fastapi_app = FastAPIServer(app)

        import uvicorn

        config = uvicorn.Config(
            fastapi_app.app,
            host=host,
            port=port,
            log_level="info",
        )
        server = uvicorn.Server(config)

        logger.info(f"Starting Browser Use Cloud MCP Server on http://{host}:{port}")
        await server.serve()

    except ImportError as e:
        logger.error(
            "HTTP transport requires additional dependencies. Install with: pip install 'browser-use-cloud-mcp[http]'"
        )
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Browser Use Cloud MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run with stdio transport
  %(prog)s --transport http             # Run with HTTP transport on localhost:8000
  %(prog)s --transport http --port 9000 # Run with HTTP transport on localhost:9000
  %(prog)s --transport http --host 0.0.0.0 --port 8000  # Run with HTTP transport on all interfaces
        """,
    )

    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport method to use (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to for HTTP transport (default: localhost)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to for HTTP transport (default: 8000)",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)",
    )

    args = parser.parse_args()

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )

    # Check if API key is available
    import os

    if not os.getenv("BROWSER_USE_CLOUD_API_KEY"):
        logger.error("BROWSER_USE_CLOUD_API_KEY environment variable is required")
        sys.exit(1)

    try:
        if args.transport == "stdio":
            asyncio.run(run_stdio())
        elif args.transport == "http":
            asyncio.run(run_http(args.host, args.port))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
