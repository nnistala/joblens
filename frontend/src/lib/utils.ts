import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";
import { formatDistanceToNow, parseISO } from "date-fns";

/**
 * Merge Tailwind CSS classes without conflicts.
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

/**
 * Format a salary range for display.
 * For INR the convention is Lakhs Per Annum (LPA).
 */
export function formatSalary(
  min: number | null,
  max: number | null,
  currency: string = "INR"
): string {
  if (min === null && max === null) return "Not disclosed";

  const fmt = (v: number): string => {
    if (currency === "INR") {
      // Assume the API stores annual salary in INR; convert to LPA
      const lpa = v / 100_000;
      return `${lpa % 1 === 0 ? lpa.toFixed(0) : lpa.toFixed(1)}`;
    }
    return v.toLocaleString("en-IN");
  };

  const symbol = currency === "INR" ? "\u20B9" : "$";
  const suffix = currency === "INR" ? " LPA" : "/yr";

  if (min !== null && max !== null) {
    return `${symbol}${fmt(min)} - ${symbol}${fmt(max)}${suffix}`;
  }
  if (min !== null) return `${symbol}${fmt(min)}+${suffix}`;
  return `Up to ${symbol}${fmt(max!)}${suffix}`;
}

/**
 * Relative date formatting ("2 days ago").
 */
export function formatDate(date: string): string {
  try {
    return formatDistanceToNow(parseISO(date), { addSuffix: true });
  } catch {
    return date;
  }
}

/**
 * Truncate a string and append an ellipsis.
 */
export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length).trimEnd() + "\u2026";
}
