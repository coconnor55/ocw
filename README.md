# O'Connor Works

Apex landing site for [oconnorworks.com](https://oconnorworks.com).

- Full-screen OCW hero image
- Hamburger menu → SpeedMyReading (`https://speedmyreading.oconnorworks.com`)
- Deployed on Vercel project **ocw**

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
