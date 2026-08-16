import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const hostname = request.headers.get("host") || "";

  // Handle fern.mutatedterrarium.com subdomain
  if (hostname.startsWith("fern.")) {
    const url = request.nextUrl.clone();

    // If already on /fern path, continue
    if (url.pathname.startsWith("/fern")) {
      return NextResponse.next();
    }

    // If on root or any other path, rewrite to /fern
    if (url.pathname === "/" || !url.pathname.startsWith("/_next")) {
      url.pathname = "/fern";
      return NextResponse.rewrite(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
