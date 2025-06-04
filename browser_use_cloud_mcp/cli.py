"""CLI entry point for the Browser Use Cloud MCP Server."""

import argparse
import asyncio
import logging
import sys
from typing import Optional

from mcp.server.models import InitializationOptions

from .server import app

logger = logging.getLogger(__name__)


def FastAPIServer(*args, **kwargs):
    """Dynamically import and create FastAPIServer instance."""
    try:
        from mcp.server.fastapi import FastAPIServer as _FastAPIServer

        return _FastAPIServer(*args, **kwargs)
    except ImportError as e:
        raise ImportError("No module named 'mcp.server.fastapi'") from e


def stdio_server():
    """Dynamically import and return stdio_server."""
    try:
        from mcp.server.stdio import stdio_server as _stdio_server

        return _stdio_server()
    except ImportError as e:
        raise ImportError("No module named 'mcp.server.stdio'") from e


class UvicornImporter:
    """Lazy importer for uvicorn to allow testing."""

    def __getattr__(self, name):
        try:
            import uvicorn as _uvicorn

            return getattr(_uvicorn, name)
        except ImportError as e:
            raise ImportError("No module named 'uvicorn'") from e


uvicorn = UvicornImporter()


async def run_stdio():
    """Run the server with stdio transport."""
    from mcp.types import ServerCapabilities, ToolsCapability
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-use-cloud-mcp",
                server_version="0.1.0",
                capabilities=ServerCapabilities(
                    tools=ToolsCapability()
                ),
            ),
        )


async def run_http(host: str = "localhost", port: int = 8000):
    """Run the server with HTTP transport."""
    try:
        fastapi_app = FastAPIServer(app)

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
        error_msg = "HTTP transport requires additional dependencies. Install with: pip install 'browser-use-cloud-mcp[http]'"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start HTTP server: {e}")
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
        error_msg = "BROWSER_USE_CLOUD_API_KEY environment variable is required"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    # Validate default model if provided
    default_model = os.getenv("BROWSER_USE_CLOUD_DEFAULT_MODEL")
    if default_model:
        from .models import LLMModel
        try:
            LLMModel(default_model)
            logger.info(f"Using default model: {default_model}")
        except ValueError:
            valid_models = [model.value for model in LLMModel]
            error_msg = f"Invalid BROWSER_USE_CLOUD_DEFAULT_MODEL '{default_model}'. Valid models are: {', '.join(valid_models)}"
            logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            sys.exit(1)

    try:
        if args.transport == "stdio":
            asyncio.run(run_stdio())
        elif args.transport == "http":
            asyncio.run(run_http(args.host, args.port))
    except KeyboardInterrupt:
        info_msg = "Server stopped by user"
        logger.info(info_msg)
        print(info_msg, file=sys.stderr)
    except Exception as e:
        error_msg = f"Server error: {e}"
        logger.error(error_msg, exc_info=True)
        print(error_msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
