# ☁️ Cloudflare Setup for CloutScape.org

To deploy permanently with Cloudflare, follow these steps:

## 1. DNS Configuration
In your Cloudflare Dashboard, add the following records:

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A    | @    | [Your VPS IP] | 🟠 Proxied |
| CNAME| www  | cloutscape.org | 🟠 Proxied |

## 2. SSL/TLS Settings
1. Go to **SSL/TLS -> Overview**.
2. Set encryption mode to **Full (Strict)**.
3. Go to **SSL/TLS -> Origin Server**.
4. Click **Create Certificate**.
5. Keep default settings (RSA 2048, 15 years).
6. **Copy the Origin Certificate** and save it as `platform/ssl/cloutscape.crt`.
7. **Copy the Private Key** and save it as `platform/ssl/cloutscape.key`.

## 3. Security Rules (Optional but Recommended)
1. Go to **Security -> WAF -> Custom Rules**.
2. Create a rule to block all traffic NOT coming from Cloudflare IP ranges to your VPS port 443.

## 4. Deployment
Once the files are in place on your VPS:
```bash
cd platform
docker-compose --profile production up -d
```

---
*Note: Cloudflare handles the SSL between the user and Cloudflare, and the Origin Certificate handles the SSL between Cloudflare and your VPS.*
