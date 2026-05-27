"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import {
  Bookmark,
  Bell,
  UserCircle,
  Trash2,
  Plus,
  Briefcase,
  MapPin,
} from "lucide-react";
import {
  getSavedJobs,
  unsaveJob,
  getAlerts,
  deleteAlert,
  createAlert,
  getMe,
} from "@/lib/api";
import { formatDate, formatSalary, cn } from "@/lib/utils";
import type { JobBrief, JobAlert, CreateAlertPayload } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<"saved" | "alerts" | "profile">("saved");
  const [showAlertForm, setShowAlertForm] = useState(false);
  const [alertForm, setAlertForm] = useState<CreateAlertPayload>({
    name: "",
    query: "",
    location: "",
    frequency: "daily",
  });

  useEffect(() => {
    const token = localStorage.getItem("joblens_token");
    if (!token) {
      router.push("/auth");
    }
  }, [router]);

  const { data: user } = useQuery({
    queryKey: ["me"],
    queryFn: getMe,
  });

  const { data: savedJobsData, isLoading: loadingSaved } = useQuery({
    queryKey: ["savedJobs"],
    queryFn: () => getSavedJobs({ page: 1, page_size: 50 }),
  });

  const { data: alerts, isLoading: loadingAlerts } = useQuery({
    queryKey: ["alerts"],
    queryFn: getAlerts,
  });

  const unsaveMutation = useMutation({
    mutationFn: (jobId: string) => unsaveJob(jobId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["savedJobs"] }),
  });

  const deleteAlertMutation = useMutation({
    mutationFn: (alertId: string) => deleteAlert(alertId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const createAlertMutation = useMutation({
    mutationFn: (payload: CreateAlertPayload) => createAlert(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
      setShowAlertForm(false);
      setAlertForm({ name: "", query: "", location: "", frequency: "daily" });
    },
  });

  const savedJobs = savedJobsData?.items ?? [];

  const tabs = [
    { key: "saved" as const, label: "Saved Jobs", icon: Bookmark, count: savedJobsData?.total },
    { key: "alerts" as const, label: "Job Alerts", icon: Bell, count: alerts?.length },
    { key: "profile" as const, label: "Profile", icon: UserCircle },
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          {user && (
            <p className="mt-1 text-sm text-gray-500">
              Welcome back, {user.full_name || user.email}
            </p>
          )}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Saved Jobs</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">
            {savedJobsData?.total ?? 0}
          </p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Active Alerts</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">
            {alerts?.filter((a) => a.is_active).length ?? 0}
          </p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <p className="text-sm text-gray-500">Applications</p>
          <p className="mt-1 text-2xl font-bold text-gray-900">0</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="mt-8 flex gap-1 border-b border-gray-200">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={cn(
              "flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors",
              activeTab === tab.key
                ? "border-primary-600 text-primary-600"
                : "border-transparent text-gray-500 hover:text-gray-700"
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {tab.count !== undefined && (
              <span className="rounded-full bg-gray-100 px-1.5 py-0.5 text-xs">
                {tab.count ?? 0}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Saved Jobs Tab */}
      {activeTab === "saved" && (
        <div className="mt-6">
          {loadingSaved ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div
                  key={i}
                  className="h-20 animate-pulse rounded-xl border border-gray-200 bg-gray-50"
                />
              ))}
            </div>
          ) : savedJobs.length > 0 ? (
            <div className="space-y-3">
              {savedJobs.map((job: JobBrief) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4"
                >
                  <Link href={`/jobs/${job.id}`} className="min-w-0 flex-1">
                    <h3 className="truncate font-medium text-gray-900 hover:text-primary-600">
                      {job.title}
                    </h3>
                    <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <Briefcase className="h-3.5 w-3.5" />
                        {job.company_name}
                      </span>
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {job.location}
                      </span>
                      {(job.salary_min || job.salary_max) && (
                        <span>
                          {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
                        </span>
                      )}
                    </div>
                  </Link>
                  <button
                    onClick={() => unsaveMutation.mutate(job.id)}
                    className="ml-4 shrink-0 rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-500"
                    aria-label="Remove saved job"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-white py-16 text-center">
              <Bookmark className="mx-auto h-10 w-10 text-gray-300" />
              <p className="mt-3 text-sm font-medium text-gray-900">
                No saved jobs yet
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Save jobs while browsing to find them here later.
              </p>
              <Link
                href="/jobs"
                className="mt-4 inline-block rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                Browse Jobs
              </Link>
            </div>
          )}
        </div>
      )}

      {/* Alerts Tab */}
      {activeTab === "alerts" && (
        <div className="mt-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900">Your Alerts</h2>
            <button
              onClick={() => setShowAlertForm(true)}
              className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
            >
              <Plus className="h-4 w-4" />
              New Alert
            </button>
          </div>

          {/* Create alert form */}
          {showAlertForm && (
            <div className="mb-6 rounded-xl border border-primary-200 bg-primary-50 p-5">
              <h3 className="mb-4 text-sm font-semibold text-gray-900">
                Create Job Alert
              </h3>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  createAlertMutation.mutate(alertForm);
                }}
                className="space-y-3"
              >
                <input
                  type="text"
                  placeholder="Alert name (e.g., Frontend jobs in Bangalore)"
                  required
                  value={alertForm.name}
                  onChange={(e) =>
                    setAlertForm((prev) => ({ ...prev, name: e.target.value }))
                  }
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                />
                <div className="flex gap-3">
                  <input
                    type="text"
                    placeholder="Search query"
                    value={alertForm.query}
                    onChange={(e) =>
                      setAlertForm((prev) => ({ ...prev, query: e.target.value }))
                    }
                    className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                  <input
                    type="text"
                    placeholder="Location"
                    value={alertForm.location}
                    onChange={(e) =>
                      setAlertForm((prev) => ({ ...prev, location: e.target.value }))
                    }
                    className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
                <select
                  value={alertForm.frequency}
                  onChange={(e) =>
                    setAlertForm((prev) => ({
                      ...prev,
                      frequency: e.target.value as "daily" | "weekly" | "instant",
                    }))
                  }
                  className="rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
                >
                  <option value="instant">Instant</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </select>
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={createAlertMutation.isPending}
                    className="rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60"
                  >
                    {createAlertMutation.isPending ? "Creating..." : "Create Alert"}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAlertForm(false)}
                    className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {loadingAlerts ? (
            <div className="space-y-3">
              {Array.from({ length: 2 }).map((_, i) => (
                <div
                  key={i}
                  className="h-20 animate-pulse rounded-xl border border-gray-200 bg-gray-50"
                />
              ))}
            </div>
          ) : alerts && alerts.length > 0 ? (
            <div className="space-y-3">
              {alerts.map((alert: JobAlert) => (
                <div
                  key={alert.id}
                  className="flex items-center justify-between rounded-xl border border-gray-200 bg-white p-4"
                >
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900">{alert.name}</h3>
                      <span
                        className={cn(
                          "rounded-full px-2 py-0.5 text-xs font-medium",
                          alert.is_active
                            ? "bg-green-100 text-green-700"
                            : "bg-gray-100 text-gray-500"
                        )}
                      >
                        {alert.is_active ? "Active" : "Paused"}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-gray-500">
                      {alert.query && `"${alert.query}"`}
                      {alert.location && ` in ${alert.location}`}
                      {" -- "}
                      {alert.frequency}
                    </p>
                    <p className="mt-0.5 text-xs text-gray-400">
                      Created {formatDate(alert.created_at)}
                    </p>
                  </div>
                  <button
                    onClick={() => deleteAlertMutation.mutate(alert.id)}
                    className="shrink-0 rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-500"
                    aria-label="Delete alert"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-200 bg-white py-16 text-center">
              <Bell className="mx-auto h-10 w-10 text-gray-300" />
              <p className="mt-3 text-sm font-medium text-gray-900">
                No job alerts yet
              </p>
              <p className="mt-1 text-sm text-gray-500">
                Create alerts to get notified about new jobs matching your criteria.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === "profile" && (
        <div className="mt-6">
          <div className="rounded-xl border border-gray-200 bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold text-gray-900">
              Profile Settings
            </h2>
            {user ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Full Name
                  </label>
                  <p className="mt-1 text-sm text-gray-900">
                    {user.full_name || "Not set"}
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Email
                  </label>
                  <p className="mt-1 text-sm text-gray-900">{user.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Account Type
                  </label>
                  <p className="mt-1 text-sm capitalize text-gray-900">{user.role}</p>
                </div>
                <p className="text-sm text-gray-500">
                  Profile editing (preferred locations, skills, resume upload) coming soon.
                </p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">Loading profile...</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
