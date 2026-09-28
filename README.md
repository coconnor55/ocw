# O'Connor Works

Apex landing site for [oconnorworks.com](https://oconnorworks.com).

- Full-screen OCW hero image
- Hamburger menu → SpeedMyReading retired page (`/speedmyreading`)
- Host rewrite: `speedmyreading.oconnorworks.com`, `speedmyreading.com`, `www.speedmyreading.com` → same retired page
- Deployed on Vercel project **ocw**

Add those hostnames on the **ocw** Vercel project and point DNS to Vercel (see SpeedMyReading `docs/public-url-retirement.md`).

## Develop

```bash
npm install
npm run dev
```

Open http://localhost:3000

## DNS (Cloudflare)

| Host | Type | Value |
|------|------|--------|
| `@` | A | `76.76.21.21` |
| `www` | CNAME | `cname.vercel-dns.com` |

Keep Cloudflare proxy (orange cloud) on; SSL mode **Full**.

Replaces the legacy `temp-ocw` project and old Netlify apex origin.
