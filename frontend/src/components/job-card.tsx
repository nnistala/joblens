"use client";

import Link from "next/link";
import Image from "next/image";
import { Heart, MapPin, Briefcase, Layers } from "lucide-react";
import { cn, formatSalary, formatDate, truncate } from "@/lib/utils";
import type { JobBrief } from "@/types";

const WORK_MODE_COLORS: Record<string, string> = {
  remote: "bg-green-100 text-green-700",
  hybrid: "bg-blue-100 text-blue-700",
  onsite: "bg-orange-100 text-orange-700",
};

const JOB_TYPE_LABELS: Record<string, string> = {
  full_time: "Full Time",
  part_time: "Part Time",
  contract: "Contract",
  internship: "Internship",
};

interface JobCardProps {
  job: JobBrief;
  onSave?: (jobId: string) => void;
  isSaved?: boolean;
}

export default function JobCard({ job, onSave, isSaved = false }: JobCardProps) {
  return (
    <div className="group relative rounded-xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md">
      <div className="flex gap-4">
        {/* Company logo */}
        <div className="hidden shrink-0 sm:block">
          {job.company_logo ? (
            <Image
              src={job.company_logo}
              alt={job.company_name}
              width={48}
              height={48}
              className="rounded-lg border border-gray-100 object-contain"
            />
          ) : (
            <div className="flex h-12 w-12 items-center justify-center rounded-lg border border-gray-100 bg-gray-50 text-lg font-semibold text-gray-400">
              {job.company_name.charAt(0)}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div>
              <Link
                href={`/jobs/${job.id}`}
                className="text-base font-semibold text-gray-900 hover:text-primary-600"
              >
                {job.title}
              </Link>
              <p className="mt-0.5 text-sm text-gray-600">{job.company_name}</p>
            </div>

            {/* Save button */}
            <button
              onClick={(e) => {
                e.preventDefault();
                onSave?.(job.id);
              }}
              className="shrink-0 rounded-full p-1.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-red-500"
              aria-label={isSaved ? "Unsave job" : "Save job"}
            >
              <Heart
                className={cn("h-5 w-5", isSaved && "fill-red-500 text-red-500")}
              />
            </button>
          </div>

          {/* Meta row */}
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <MapPin className="h-3.5 w-3.5" />
              {job.location}
            </span>
            <span className="flex items-center gap-1">
              <Briefcase className="h-3.5 w-3.5" />
              {JOB_TYPE_LABELS[job.job_type] || job.job_type}
            </span>
            {(job.salary_min || job.salary_max) && (
              <span>
                {formatSalary(job.salary_min, job.salary_max, job.salary_currency)}
              </span>
            )}
          </div>

          {/* Badges */}
          <div className="mt-3 flex flex-wrap items-center gap-2">
            <span
              className={cn(
                "inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
                WORK_MODE_COLORS[job.work_mode] || "bg-gray-100 text-gray-700"
              )}
            >
              {job.work_mode}
            </span>

            {/* Skills */}
            {job.skills.slice(0, 5).map((skill) => (
              <span
                key={skill}
                className="inline-flex rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600"
              >
                {truncate(skill, 20)}
              </span>
            ))}
            {job.skills.length > 5 && (
              <span className="text-xs text-gray-400">
                +{job.skills.length - 5} more
              </span>
            )}
          </div>

          {/* Footer */}
          <div className="mt-3 flex items-center justify-between text-xs text-gray-400">
            <span>{formatDate(job.posted_at)}</span>
            {job.source_count > 1 && (
              <span className="flex items-center gap-1 rounded-full bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-700">
                <Layers className="h-3 w-3" />
                Found on {job.source_count} sources
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
