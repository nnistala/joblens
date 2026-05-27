"use client";

import { useState } from "react";
import { CheckCircle, Globe, BarChart3, Zap } from "lucide-react";
import { registerCompany } from "@/lib/api";

const ATS_PLATFORMS = [
  "Greenhouse",
  "Lever",
  "Workday",
  "Taleo",
  "SAP SuccessFactors",
  "iCIMS",
  "BambooHR",
  "SmartRecruiters",
  "Freshteam",
  "Zoho Recruit",
  "Darwinbox",
  "Custom / Other",
];

const BENEFITS = [
  {
    icon: Globe,
    title: "Reach More Candidates",
    description:
      "Your open positions are automatically surfaced to thousands of active job seekers across India.",
  },
  {
    icon: BarChart3,
    title: "Analytics & Insights",
    description:
      "Track how many views and applications your listings receive directly from JobLens.",
  },
  {
    icon: Zap,
    title: "Zero Cost, Zero Effort",
    description:
      "Your career page stays in sync automatically. No manual posting. No subscription fees. Completely free.",
  },
];

export default function HRPage() {
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    company_name: "",
    career_page_url: "",
    ats_platform: "",
    feed_url: "",
    contact_name: "",
    contact_email: "",
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
    setError(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await registerCompany({
        company_name: form.company_name,
        career_page_url: form.career_page_url,
        ats_platform: form.ats_platform,
        feed_url: form.feed_url || undefined,
        contact_name: form.contact_name,
        contact_email: form.contact_email,
      });
      setSubmitted(true);
    } catch {
      setError("Something went wrong. Please try again or contact us directly.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900 px-4 py-16 text-center text-white sm:px-6 sm:py-24 lg:px-8">
        <div className="mx-auto max-w-3xl">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            List Your Jobs for Free
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-lg text-primary-100">
            Your open positions are automatically surfaced to thousands of
            qualified candidates across India. No manual posting required.
          </p>
        </div>
      </section>

      {/* Benefits */}
      <section className="px-4 py-16 sm:px-6 lg:px-8">
        <div className="mx-auto max-w-5xl">
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            {BENEFITS.map((benefit) => (
              <div
                key={benefit.title}
                className="rounded-xl border border-gray-200 bg-white p-6"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-50 text-primary-600">
                  <benefit.icon className="h-5 w-5" />
                </div>
                <h3 className="mt-4 text-lg font-semibold text-gray-900">
                  {benefit.title}
                </h3>
                <p className="mt-2 text-sm leading-relaxed text-gray-500">
                  {benefit.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Registration Form */}
      <section className="bg-gray-50 px-4 py-16 sm:px-6 lg:px-8" id="register">
        <div className="mx-auto max-w-xl">
          {submitted ? (
            <div className="rounded-2xl border border-green-200 bg-white p-8 text-center shadow-sm">
              <CheckCircle className="mx-auto h-12 w-12 text-green-500" />
              <h2 className="mt-4 text-2xl font-bold text-gray-900">
                Registration Submitted
              </h2>
              <p className="mt-2 text-gray-500">
                Thank you for registering {form.company_name} with JobLens. Our
                team will review your submission and your jobs will be live
                within 48 hours. We will notify you at {form.contact_email}.
              </p>
            </div>
          ) : (
            <div className="rounded-2xl border border-gray-200 bg-white p-8 shadow-sm">
              <h2 className="text-2xl font-bold text-gray-900">
                Register Your Company
              </h2>
              <p className="mt-1 text-sm text-gray-500">
                Tell us about your career page and we will start indexing your
                jobs.
              </p>

              {error && (
                <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600">
                  {error}
                </div>
              )}

              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                <div>
                  <label
                    htmlFor="company_name"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Company Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="company_name"
                    name="company_name"
                    type="text"
                    required
                    value={form.company_name}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    placeholder="Acme Corp"
                  />
                </div>

                <div>
                  <label
                    htmlFor="career_page_url"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Career Page URL <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="career_page_url"
                    name="career_page_url"
                    type="url"
                    required
                    value={form.career_page_url}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    placeholder="https://careers.acme.com"
                  />
                </div>

                <div>
                  <label
                    htmlFor="ats_platform"
                    className="block text-sm font-medium text-gray-700"
                  >
                    ATS Platform <span className="text-red-500">*</span>
                  </label>
                  <select
                    id="ats_platform"
                    name="ats_platform"
                    required
                    value={form.ats_platform}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  >
                    <option value="">Select your ATS</option>
                    {ATS_PLATFORMS.map((platform) => (
                      <option key={platform} value={platform}>
                        {platform}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="feed_url"
                    className="block text-sm font-medium text-gray-700"
                  >
                    Job Feed URL{" "}
                    <span className="text-xs text-gray-400">(optional)</span>
                  </label>
                  <input
                    id="feed_url"
                    name="feed_url"
                    type="url"
                    value={form.feed_url}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                    placeholder="https://careers.acme.com/jobs.xml"
                  />
                  <p className="mt-1 text-xs text-gray-400">
                    RSS, XML, or JSON feed if available
                  </p>
                </div>

                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label
                      htmlFor="contact_name"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Contact Name <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="contact_name"
                      name="contact_name"
                      type="text"
                      required
                      value={form.contact_name}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label
                      htmlFor="contact_email"
                      className="block text-sm font-medium text-gray-700"
                    >
                      Contact Email <span className="text-red-500">*</span>
                    </label>
                    <input
                      id="contact_email"
                      name="contact_email"
                      type="email"
                      required
                      value={form.contact_email}
                      onChange={handleChange}
                      className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                      placeholder="hr@acme.com"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-primary-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "Submitting..." : "Register Company"}
                </button>
              </form>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
