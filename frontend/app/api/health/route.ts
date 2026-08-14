import type { NextRequest } from "next/server";
import { proxyBackendRequest } from "../../../lib/api/proxy";

export async function GET(request: NextRequest) {
  return proxyBackendRequest(request, ["health"], "GET");
}

