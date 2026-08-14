import type { NextRequest } from "next/server";
import { proxyBackendRequest } from "../../../../lib/api/proxy";

interface RouteContext {
  params: Promise<{
    path: string[];
  }>;
}

async function forward(
  request: NextRequest,
  context: RouteContext,
  method: "GET" | "POST" | "DELETE",
) {
  const { path } = await context.params;
  return proxyBackendRequest(request, path, method);
}

export async function GET(request: NextRequest, context: RouteContext) {
  return forward(request, context, "GET");
}

export async function POST(request: NextRequest, context: RouteContext) {
  return forward(request, context, "POST");
}

export async function DELETE(request: NextRequest, context: RouteContext) {
  return forward(request, context, "DELETE");
}

