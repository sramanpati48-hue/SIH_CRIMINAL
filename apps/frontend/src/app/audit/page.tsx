'use client';
import React, { useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function AuditPage() {
  const router = useRouter();

  useEffect(() => {
    async function fetchAndRedirect() {
      try {
        const res = await api.listCases();
        if (res.cases && res.cases.length > 0) {
          router.push(`/cases/${res.cases[0].id}`);
        } else {
          router.push('/cases');
        }
      } catch (err) {
        router.push('/cases');
      }
    }
    fetchAndRedirect();
  }, [router]);

  return (
    <div className="flex justify-center py-20">
      <div className="animate-spin w-8 h-8 border-4 border-amber-500 border-t-transparent rounded-full"></div>
    </div>
  );
}
