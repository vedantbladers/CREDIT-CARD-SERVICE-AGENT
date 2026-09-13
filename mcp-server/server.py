import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from config import settings
from tools import (
    TOOLS_MANIFEST,
    execute_adjust_credit_limit,
    execute_get_account,
    execute_replace_card,
    execute_waive_fee,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp.server")

app = FastAPI(
    title="Credit Card Core Banking MCP Server",
    description="Model Context Protocol (MCP) server providing isolated, ACID-compliant database execution tools.",
    version=settings.SERVER_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Standard MCP JSON-RPC 2.0 Request / Response Schemas
class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = 1


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    id: Optional[Any] = 1


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.SERVER_NAME,
        "protocol": "Model Context Protocol (MCP) JSON-RPC 2.0",
        "tools_count": len(TOOLS_MANIFEST),
    }


@app.get("/tools")
def list_tools_rest():
    """List available MCP tools via REST."""
    return {"tools": TOOLS_MANIFEST}


@app.post("/mcp", response_model=JsonRpcResponse)
def handle_mcp_jsonrpc(request: JsonRpcRequest) -> JsonRpcResponse:
    """
    Standard MCP JSON-RPC 2.0 Handler:
    - 'tools/list': returns approved tools manifest
    - 'tools/call': executes approved tool with ACID transaction
    """
    method = request.method
    params = request.params or {}

    logger.info(f"MCP Request: method={method}, id={request.id}")

    if method == "tools/list":
        return JsonRpcResponse(
            jsonrpc="2.0",
            result={"tools": TOOLS_MANIFEST},
            id=request.id,
        )

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            result_content = dispatch_tool(tool_name, arguments)
            return JsonRpcResponse(
                jsonrpc="2.0",
                result={
                    "content": [
                        {
                            "type": "text",
                            "text": f"Successfully executed tool {tool_name}",
                        }
                    ],
                    "data": result_content,
                    "isError": False,
                },
                id=request.id,
            )
        except Exception as e:
            logger.error(f"Error executing MCP tool {tool_name}: {e}")
            return JsonRpcResponse(
                jsonrpc="2.0",
                error={
                    "code": -32603,
                    "message": f"Execution failed for tool '{tool_name}': {str(e)}",
                },
                id=request.id,
            )

    else:
        return JsonRpcResponse(
            jsonrpc="2.0",
            error={
                "code": -32601,
                "message": f"Method '{method}' not found. Supported methods: 'tools/list', 'tools/call'.",
            },
            id=request.id,
        )


@app.post("/tools/{tool_name}")
def call_tool_rest(tool_name: str, arguments: Dict[str, Any]):
    """Direct REST invocation of an approved MCP tool."""
    try:
        return dispatch_tool(tool_name, arguments)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")


def dispatch_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatches execution to approved tool functions."""
    if tool_name == "waive_fee":
        return execute_waive_fee(
            account_id=arguments["account_id"],
            amount=arguments.get("amount"),
            fee_type=arguments.get("fee_type", "annual_fee"),
        )
    elif tool_name == "adjust_credit_limit":
        return execute_adjust_credit_limit(
            account_id=arguments["account_id"],
            new_limit=arguments["new_limit"],
        )
    elif tool_name == "replace_card":
        return execute_replace_card(
            account_id=arguments["account_id"],
            reason=arguments.get("reason", "stolen"),
            delivery_type=arguments.get("delivery_type", "standard"),
        )
    elif tool_name == "get_account":
        return execute_get_account(account_id=arguments["account_id"])
    else:
        raise ValueError(f"Unknown or unauthorized MCP tool: '{tool_name}'")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=settings.HOST, port=settings.PORT, reload=True)
