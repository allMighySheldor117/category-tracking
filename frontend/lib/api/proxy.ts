import { NextResponse, type NextRequest } from "next/server";

const DEFAULT_BACKEND_BASE_URL = "http://127.0.0.1:8000";

export function getBackendBaseUrl(): string {
  return process.env.FRONTEND_API_BASE_URL ?? DEFAULT_BACKEND_BASE_URL;
}

function buildBackendUrl(pathSegments: string[], search: string): string {
  const baseUrl = getBackendBaseUrl().replace(/\/$/, "");
  const safePath = pathSegments
    .map((segment) => encodeURIComponent(segment))
    .join("/");
  return `${baseUrl}/${safePath}${search}`;
}

function transportError(status: number, message: string) {
  return NextResponse.json(
    {
      error: {
        code: "frontend_transport_error",
        message,
        details: null,
      },
    },
    { status },
  );
}

export async function proxyBackendRequest(
  request: NextRequest,
  pathSegments: string[],
  method: "GET" | "POST" | "DELETE",
): Promise<NextResponse> {
  const targetUrl = buildBackendUrl(pathSegments, request.nextUrl.search);
  const body = method === "GET" ? undefined : await request.text();

  try {
    const backendResponse = await fetch(targetUrl, {
      method,
      headers:
        body === undefined
          ? { Accept: "application/json" }
          : {
              Accept: "application/json",
              "Content-Type": request.headers.get("content-type") ?? "application/json",
            },
      body: body === "" ? undefined : body,
      cache: "no-store",
    });

    const responseBody = await backendResponse.text();
    return new NextResponse(responseBody, {
      status: backendResponse.status,
      headers: {
        "Content-Type":
          backendResponse.headers.get("content-type") ?? "application/json",
      },
    });
  } catch {
    return transportError(502, "Backend service is unavailable.");
  }
}

