"use client";

import { FormEvent, useEffect, useState } from "react";
import { CheckCircle2, CreditCard, Dumbbell, Loader2, Smartphone } from "lucide-react";
import { api, ApiError } from "@/lib/api-client";
import { MembershipPlan } from "@/types/api";

interface SignupPageProps {
  params: { gymId: string };
}

interface PublicSignupResponse {
  member: { name: string };
  membership: { plan_name?: string | null };
  payment: { status: string };
}

export default function PublicSignupPage({ params }: SignupPageProps) {
  const [plans, setPlans] = useState<MembershipPlan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("upi");
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    city: "",
    fitness_goal: "",
  });
  const [isLoadingPlans, setIsLoadingPlans] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState<PublicSignupResponse | null>(null);

  useEffect(() => {
    api
      .get<{ items: MembershipPlan[] }>(`/public/gyms/${params.gymId}/plans`)
      .then((data) => {
        setPlans(data.items);
        setSelectedPlan(data.items[0]?.id || "");
      })
      .catch((requestError: ApiError) => {
        setError(requestError.detail || "We could not load this gym's plans.");
      })
      .finally(() => setIsLoadingPlans(false));
  }, [params.gymId]);

  const updateField = (field: keyof typeof form, value: string) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const submitSignup = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const data = await api.post<PublicSignupResponse>("/public/member-signup", {
        gym_id: params.gymId,
        plan_id: selectedPlan,
        member: { ...form, status: "active" },
        payment_method: paymentMethod,
        payment_status: "success",
      });
      setSuccess(data);
    } catch (requestError) {
      const apiError = requestError as ApiError;
      setError(apiError.detail || "Payment could not be completed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const chosenPlan = plans.find((plan) => plan.id === selectedPlan);

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4 py-12 text-white">
        <section className="w-full max-w-lg rounded-2xl border border-emerald-500/30 bg-zinc-900 p-8 text-center shadow-2xl shadow-emerald-950/30">
          <CheckCircle2 className="mx-auto h-16 w-16 text-emerald-400" />
          <p className="mt-6 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-400">Payment confirmed</p>
          <h1 className="mt-3 text-3xl font-bold">Welcome to FitFlow</h1>
          <p className="mt-3 text-zinc-400">
            {success.member.name}, your {success.membership.plan_name || "membership"} is active.
          </p>
          <p className="mt-6 rounded-lg bg-zinc-950 px-4 py-3 text-sm text-zinc-300">
            Your details and payment have been registered with the gym.
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 px-4 py-10 text-white sm:px-6">
      <div className="mx-auto max-w-5xl">
        <header className="mb-8 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-600/25">
            <Dumbbell className="h-5 w-5" />
          </div>
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-300">FitFlow membership</p>
            <h1 className="text-2xl font-bold">Join your gym</h1>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <form onSubmit={submitSignup} className="rounded-2xl border border-zinc-800 bg-zinc-900/80 p-6 shadow-xl sm:p-8">
            <div className="mb-7">
              <p className="text-sm text-zinc-400">Step 1</p>
              <h2 className="mt-1 text-xl font-semibold">Your details</h2>
            </div>

            {error && <div className="mb-5 rounded-lg border border-red-900/60 bg-red-950/40 p-3 text-sm text-red-300">{error}</div>}

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="sm:col-span-2">
                <span className="mb-1.5 block text-sm text-zinc-300">Full name</span>
                <input required value={form.name} onChange={(event) => updateField("name", event.target.value)} className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 outline-none focus:border-indigo-500" />
              </label>
              <label>
                <span className="mb-1.5 block text-sm text-zinc-300">Email</span>
                <input required type="email" value={form.email} onChange={(event) => updateField("email", event.target.value)} className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 outline-none focus:border-indigo-500" />
              </label>
              <label>
                <span className="mb-1.5 block text-sm text-zinc-300">Phone</span>
                <input required minLength={7} value={form.phone} onChange={(event) => updateField("phone", event.target.value)} className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 outline-none focus:border-indigo-500" />
              </label>
              <label>
                <span className="mb-1.5 block text-sm text-zinc-300">City</span>
                <input value={form.city} onChange={(event) => updateField("city", event.target.value)} className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 outline-none focus:border-indigo-500" />
              </label>
              <label>
                <span className="mb-1.5 block text-sm text-zinc-300">Fitness goal</span>
                <select value={form.fitness_goal} onChange={(event) => updateField("fitness_goal", event.target.value)} className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2.5 outline-none focus:border-indigo-500">
                  <option value="">Choose a goal</option>
                  <option>Weight Loss</option>
                  <option>Muscle Gain</option>
                  <option>Endurance</option>
                  <option>General Fitness</option>
                </select>
              </label>
            </div>

            <div className="mt-8 border-t border-zinc-800 pt-7">
              <p className="text-sm text-zinc-400">Step 2</p>
              <h2 className="mt-1 text-xl font-semibold">Choose a plan</h2>
              {isLoadingPlans ? (
                <div className="mt-5 flex items-center gap-2 text-sm text-zinc-400"><Loader2 className="h-4 w-4 animate-spin" /> Loading plans...</div>
              ) : plans.length === 0 ? (
                <p className="mt-5 text-sm text-zinc-400">This gym has no active plans available yet.</p>
              ) : (
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {plans.map((plan) => (
                    <label key={plan.id} className={`cursor-pointer rounded-xl border p-4 transition ${selectedPlan === plan.id ? "border-indigo-500 bg-indigo-500/10" : "border-zinc-700 bg-zinc-950 hover:border-zinc-500"}`}>
                      <input type="radio" name="plan" value={plan.id} checked={selectedPlan === plan.id} onChange={() => setSelectedPlan(plan.id)} className="sr-only" />
                      <span className="flex items-start justify-between gap-3">
                        <span><span className="block font-semibold">{plan.name}</span><span className="mt-1 block text-xs text-zinc-400">{plan.duration_days} days</span></span>
                        <span className="font-semibold text-indigo-300">₹{plan.price.toLocaleString("en-IN")}</span>
                      </span>
                    </label>
                  ))}
                </div>
              )}
            </div>

            <div className="mt-8 border-t border-zinc-800 pt-7">
              <p className="text-sm text-zinc-400">Step 3</p>
              <h2 className="mt-1 text-xl font-semibold">Payment method</h2>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <button type="button" onClick={() => setPaymentMethod("upi")} className={`flex items-center justify-center gap-2 rounded-lg border px-3 py-3 text-sm ${paymentMethod === "upi" ? "border-emerald-500 bg-emerald-500/10 text-emerald-300" : "border-zinc-700 text-zinc-400"}`}><Smartphone className="h-4 w-4" /> UPI</button>
                <button type="button" onClick={() => setPaymentMethod("card")} className={`flex items-center justify-center gap-2 rounded-lg border px-3 py-3 text-sm ${paymentMethod === "card" ? "border-emerald-500 bg-emerald-500/10 text-emerald-300" : "border-zinc-700 text-zinc-400"}`}><CreditCard className="h-4 w-4" /> Card</button>
              </div>
            </div>

            <button type="submit" disabled={isSubmitting || !chosenPlan || isLoadingPlans} className="mt-8 flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-3 font-semibold transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50">
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              {isSubmitting ? "Processing payment..." : `Pay ₹${chosenPlan?.price.toLocaleString("en-IN") || "0"} and join`}
            </button>
          </form>

          <aside className="h-fit rounded-2xl border border-zinc-800 bg-zinc-900 p-6 lg:sticky lg:top-6">
            <p className="text-sm text-zinc-400">Membership summary</p>
            <h2 className="mt-2 text-2xl font-bold">{chosenPlan?.name || "Select a plan"}</h2>
            <div className="mt-6 space-y-3 border-t border-zinc-800 pt-5 text-sm">
              <div className="flex justify-between text-zinc-400"><span>Duration</span><span className="text-zinc-200">{chosenPlan ? `${chosenPlan.duration_days} days` : "-"}</span></div>
              <div className="flex justify-between text-zinc-400"><span>Payment</span><span className="capitalize text-zinc-200">{paymentMethod}</span></div>
              <div className="flex justify-between pt-3 text-base font-semibold"><span>Total</span><span className="text-indigo-300">₹{chosenPlan?.price.toLocaleString("en-IN") || "0"}</span></div>
            </div>
            <p className="mt-6 text-xs leading-5 text-zinc-500">Your membership is registered only after the payment is confirmed.</p>
          </aside>
        </div>
      </div>
    </main>
  );
}
