export default async function handler(req, res) {
  const hook = process.env.VERCEL_DEPLOY_HOOK_URL;

  if (!hook) {
    return res.status(200).json({
      ok: false,
      message: "VERCEL_DEPLOY_HOOK_URL not set; cron received",
    });
  }

  try {
    const resp = await fetch(hook, { method: "POST" });
    const text = await resp.text();
    return res.status(200).json({ ok: true, status: resp.status, body: text });
  } catch (err) {
    return res.status(500).json({ ok: false, error: String(err) });
  }
}
