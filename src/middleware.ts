import { NextRequest, NextResponse } from "next/server";

const RETIRED_HOSTS = new Set([
  "speedmyreading.oconnorworks.com",
  "speedmyreading.com",
  "www.speedmyreading.com",
]);

export function middleware(request: NextRequest) {
  const host = request.headers.get("host")?.split(":")[0]?.toLowerCase();

  if (host && RETIRED_HOSTS.has(host)) {
    const url = request.nextUrl.clone();
    if (url.pathname !== "/speedmyreading") {
      url.pathname = "/speedmyreading";
      return NextResponse.rewrite(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
