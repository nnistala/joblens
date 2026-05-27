"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Search, MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

const INDIAN_CITIES = [
  "All Locations",
  "Bangalore",
  "Mumbai",
  "Delhi NCR",
  "Hyderabad",
  "Chennai",
  "Pune",
  "Kolkata",
  "Remote",
];

interface SearchBarProps {
  initialQuery?: string;
  initialLocation?: string;
  className?: string;
  size?: "default" | "large";
}

export default function SearchBar({
  initialQuery = "",
  initialLocation = "",
  className,
  size = "default",
}: SearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [location, setLocation] = useState(initialLocation);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (location && location !== "All Locations") params.set("location", location);
    router.push(`/jobs?${params.toString()}`);
  };

  const isLarge = size === "large";

  return (
    <form
      onSubmit={handleSubmit}
      className={cn(
        "flex w-full flex-col gap-3 rounded-xl border border-gray-200 bg-white p-2 shadow-sm sm:flex-row sm:items-center",
        isLarge && "sm:p-3 lg:p-4",
        className
      )}
    >
      {/* Query input */}
      <div className="flex flex-1 items-center gap-2 px-3">
        <Search
          className={cn(
            "shrink-0 text-gray-400",
            isLarge ? "h-5 w-5" : "h-4 w-4"
          )}
        />
        <input
          type="text"
          placeholder="Job title, skills, or company"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={cn(
            "w-full border-0 bg-transparent text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-0",
            isLarge ? "py-3 text-lg" : "py-2 text-sm"
          )}
        />
      </div>

      {/* Divider */}
      <div className="hidden h-8 w-px bg-gray-200 sm:block" />

      {/* Location select */}
      <div className="flex items-center gap-2 px-3">
        <MapPin
          className={cn(
            "shrink-0 text-gray-400",
            isLarge ? "h-5 w-5" : "h-4 w-4"
          )}
        />
        <select
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className={cn(
            "w-full min-w-[140px] border-0 bg-transparent text-gray-900 focus:outline-none focus:ring-0 sm:w-auto",
            isLarge ? "py-3 text-lg" : "py-2 text-sm"
          )}
        >
          {INDIAN_CITIES.map((city) => (
            <option key={city} value={city === "All Locations" ? "" : city}>
              {city}
            </option>
          ))}
        </select>
      </div>

      {/* Search button */}
      <button
        type="submit"
        className={cn(
          "shrink-0 rounded-lg bg-primary-600 font-medium text-white transition-colors hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2",
          isLarge ? "px-8 py-3 text-base" : "px-6 py-2 text-sm"
        )}
      >
        Search Jobs
      </button>
    </form>
  );
}
