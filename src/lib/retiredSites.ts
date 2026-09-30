export type RetiredSite = {
  label: string;
  route: string;
  hosts: readonly string[];
};

/** Single owner for retired public sites (menu + host rewrite). */
export const RETIRED_SITES: readonly RetiredSite[] = [
  {
    label: "SpeedMyReading",
    route: "/speedmyreading",
    hosts: [
      "speedmyreading.oconnorworks.com",
      "speedmyreading.com",
      "www.speedmyreading.com",
    ],
  },
  {
    label: "Battle for the Oceans",
    route: "/battlefortheoceans",
    hosts: ["battlefortheoceans.com", "www.battlefortheoceans.com"],
  },
] as const;

const HOST_TO_ROUTE = new Map<string, string>(
  RETIRED_SITES.flatMap((site) => site.hosts.map((host) => [host, site.route])),
);

const RETIRED_ROUTES = new Set(RETIRED_SITES.map((site) => site.route));

export function routeForRetiredHost(host: string | null | undefined): string | null {
  if (!host) return null;
  const bare = host.split(":")[0]?.toLowerCase();
  if (!bare) return null;
  return HOST_TO_ROUTE.get(bare) ?? null;
}

export function isRetiredRoute(pathname: string | null | undefined): boolean {
  if (!pathname) return false;
  return RETIRED_ROUTES.has(pathname);
}

export function isRetiredHost(host: string | null | undefined): boolean {
  return routeForRetiredHost(host) != null;
}
