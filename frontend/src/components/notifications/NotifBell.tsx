"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNewsStore } from "@/store/useNewsStore";
import { API_BASE } from "@/lib/api";

export function NotifBell() {
  useNewsStore();
  const [subscribed, setSubscribed] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if ("serviceWorker" in navigator && "PushManager" in window) {
      navigator.serviceWorker.ready.then(async (reg) => {
        const sub = await reg.pushManager.getSubscription();
        setSubscribed(!!sub);
      });
    }
  }, []);

  const toggleNotif = async () => {
    if (!("serviceWorker" in navigator)) return;
    setLoading(true);
    try {
      const reg = await navigator.serviceWorker.ready;
      const existing = await reg.pushManager.getSubscription();

      if (existing) {
        await fetch(`${API_BASE}/api/push/unsubscribe?endpoint=` + encodeURIComponent(existing.endpoint), { method: "DELETE" });
        await existing.unsubscribe();
        setSubscribed(false);
      } else {
        const keyRes = await fetch(`${API_BASE}/api/push/vapid-key`);
        const { publicKey } = await keyRes.json();
        if (!publicKey) return;

        const sub = await reg.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: publicKey,
        });
        const json = sub.toJSON();
        await fetch(`${API_BASE}/api/push/subscribe`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ endpoint: sub.endpoint, keys: json.keys }),
        });
        setSubscribed(true);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={toggleNotif}
      disabled={loading}
      className="w-9 h-9 rounded-xl glass flex items-center justify-center relative transition-colors hover:text-white"
      title={subscribed ? "Wyłącz powiadomienia" : "Włącz powiadomienia"}
    >
      <motion.span
        className="text-lg"
        animate={subscribed ? { rotate: [0, -10, 10, -5, 5, 0] } : {}}
        transition={{ duration: 0.4 }}
      >
        {subscribed ? "🔔" : "🔕"}
      </motion.span>
      {subscribed && (
        <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full accent-bg" />
      )}
    </button>
  );
}
