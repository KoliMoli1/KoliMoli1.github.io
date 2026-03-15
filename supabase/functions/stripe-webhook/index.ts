// supabase/functions/stripe-webhook/index.ts
// Supabase Edge Function — Stripe webhook handler for FlowDesk subscription management

import Stripe from "https://esm.sh/stripe@14.21.0?target=deno&deno-std=0.177.0&no-check";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2?target=deno";

// ---------------------------------------------------------------------------
// Environment variables (set in Supabase dashboard → Project Settings → Edge Functions)
// ---------------------------------------------------------------------------
const STRIPE_SECRET_KEY = Deno.env.get("STRIPE_SECRET_KEY")!;
const STRIPE_WEBHOOK_SECRET = Deno.env.get("STRIPE_WEBHOOK_SECRET")!;
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

// ---------------------------------------------------------------------------
// Clients (initialised once per isolate cold-start)
// ---------------------------------------------------------------------------
const stripe = new Stripe(STRIPE_SECRET_KEY, {
  apiVersion: "2023-10-16",
  httpClient: Stripe.createFetchHttpClient(),
});

// Service-role client — bypasses RLS so we can write subscription_status safely
const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, {
  auth: { persistSession: false },
});

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Resolve a Supabase profile row ID from:
 *   1. session.metadata.supabase_user_id  (preferred — set by the payment link)
 *   2. customer email                     (fallback — look up in auth.users via admin API)
 */
async function resolveUserId(
  supabaseUserId: string | null | undefined,
  customerEmail: string | null | undefined
): Promise<string | null> {
  if (supabaseUserId) {
    return supabaseUserId;
  }

  if (customerEmail) {
    const { data: adminData, error: adminError } =
      await supabase.auth.admin.listUsers({ page: 1, perPage: 1000 });

    if (adminError) {
      console.error("admin.listUsers error:", adminError.message);
      return null;
    }

    const match = adminData.users.find(
      (u) => u.email?.toLowerCase() === customerEmail.toLowerCase()
    );
    return match?.id ?? null;
  }

  return null;
}

/**
 * Update profiles.subscription_status for a given user UUID.
 */
async function updateSubscriptionStatus(
  userId: string,
  status: "free" | "pro" | "group"
): Promise<void> {
  const { error } = await supabase
    .from("profiles")
    .update({ subscription_status: status, updated_at: new Date().toISOString() })
    .eq("id", userId);

  if (error) {
    throw new Error(
      `Failed to update subscription_status to '${status}' for user ${userId}: ${error.message}`
    );
  }

  console.log(`Set subscription_status='${status}' for user ${userId}`);
}

/**
 * Map session.metadata.plan to our internal subscription_status value.
 * Defaults to 'pro' for any unrecognised value so purchases are never silently dropped.
 */
function mapPlan(plan: string | undefined): "pro" | "group" {
  if (plan === "group") return "group";
  return "pro";
}

// ---------------------------------------------------------------------------
// Main handler
// ---------------------------------------------------------------------------
Deno.serve(async (req: Request): Promise<Response> => {
  if (req.method !== "POST") {
    return new Response("Method Not Allowed", { status: 405 });
  }

  const signature = req.headers.get("Stripe-Signature");
  if (!signature) {
    return new Response("Missing Stripe-Signature header", { status: 400 });
  }

  // Raw body is required for signature verification — must be read before parsing
  const rawBody = await req.text();

  // ---------------------------------------------------------------------------
  // 1. Verify webhook signature
  // ---------------------------------------------------------------------------
  let event: Stripe.Event;
  try {
    event = await stripe.webhooks.constructEventAsync(
      rawBody,
      signature,
      STRIPE_WEBHOOK_SECRET
    );
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("Webhook signature verification failed:", message);
    return new Response(`Webhook signature verification failed: ${message}`, {
      status: 400,
    });
  }

  console.log(`Received Stripe event: ${event.type} (id: ${event.id})`);

  // ---------------------------------------------------------------------------
  // 2. Handle events
  // ---------------------------------------------------------------------------
  try {
    switch (event.type) {
      // -----------------------------------------------------------------------
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;

        const supabaseUserId = session.metadata?.supabase_user_id;
        const customerEmail =
          session.customer_email ??
          session.customer_details?.email ??
          undefined;

        const userId = await resolveUserId(supabaseUserId, customerEmail);
        if (!userId) {
          console.error(
            `checkout.session.completed: could not resolve user — ` +
            `session=${session.id}, supabase_user_id=${supabaseUserId}, email=${customerEmail}`
          );
          // Return 200 so Stripe does not retry an unresolvable event
          break;
        }

        const plan = mapPlan(session.metadata?.plan);
        await updateSubscriptionStatus(userId, plan);
        break;
      }

      // -----------------------------------------------------------------------
      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;

        const supabaseUserId = subscription.metadata?.supabase_user_id;

        let customerEmail: string | undefined;
        if (!supabaseUserId && subscription.customer) {
          try {
            const customerId =
              typeof subscription.customer === "string"
                ? subscription.customer
                : subscription.customer.id;

            const customer = await stripe.customers.retrieve(customerId);
            if (!customer.deleted && customer.email) {
              customerEmail = customer.email;
            }
          } catch (stripeErr: unknown) {
            console.error(
              "Failed to retrieve Stripe customer:",
              stripeErr instanceof Error ? stripeErr.message : String(stripeErr)
            );
          }
        }

        const userId = await resolveUserId(supabaseUserId, customerEmail);
        if (!userId) {
          console.error(
            `customer.subscription.deleted: could not resolve user — subscription=${subscription.id}`
          );
          break;
        }

        await updateSubscriptionStatus(userId, "free");
        break;
      }

      // -----------------------------------------------------------------------
      default:
        // Stripe expects 200 for unhandled event types
        console.log(`Unhandled event type: ${event.type} — ignoring`);
        break;
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    console.error("Error processing event:", message);
    // Return 500 for internal errors so Stripe will retry
    return new Response(`Internal error: ${message}`, { status: 500 });
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});
