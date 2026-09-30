import { NextRequest, NextResponse } from "next/server";
import { routeForRetiredHost } from "./lib/retiredSites";

export function middleware(request: NextRequest) {
  const host = request.headers.get("host");
  const route = routeForRetiredHost(host);

  if (route) {
    const url = request.nextUrl.clone();
    if (url.pathname !== route) {
      url.pathname = route;
      return NextResponse.rewrite(url);
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
