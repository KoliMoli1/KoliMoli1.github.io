# stripe-webhook — Deployment Checklist

## 1. Set secrets in Supabase Dashboard → Project Settings → Edge Functions → Secrets

| Secret                      | Value                                                        |
|-----------------------------|--------------------------------------------------------------|
| `STRIPE_SECRET_KEY`         | `sk_live_...` (Stripe Dashboard → Developers → API keys)    |
| `STRIPE_WEBHOOK_SECRET`     | `whsec_...` (from the webhook endpoint after registering it) |
| `SUPABASE_URL`              | `https://teovjlyddhbiauadojsa.supabase.co`                  |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → Project Settings → API → service_role  |

> `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are also available as built-in secrets
> in Supabase Edge Functions — you may use those instead of adding them manually.

## 2. Deploy

```bash
supabase functions deploy stripe-webhook --project-ref teovjlyddhbiauadojsa
```

Deployed URL:
```
https://teovjlyddhbiauadojsa.supabase.co/functions/v1/stripe-webhook
```

## 3. Register webhook in Stripe

1. Stripe Dashboard → Developers → Webhooks → **Add endpoint**
2. Set **Endpoint URL** to the deployed URL above
3. Under **Events to send**, add exactly:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
4. Save — copy the `whsec_...` **Signing secret** → paste into `STRIPE_WEBHOOK_SECRET`

## 4. Payment Link metadata required

Each Payment Link must have metadata set in the Stripe Dashboard:

| Key                  | Value (Pro)  | Value (Study Group) |
|----------------------|--------------|---------------------|
| `plan`               | `pro`        | `group`             |
| `supabase_user_id`   | *(pass the logged-in user's Supabase UUID when available)* |

- `plan` is used by the webhook to determine which `subscription_status` value to write.
- `supabase_user_id` is the preferred user identification method. If absent, the function
  falls back to matching `customer_email` against `auth.users`.
