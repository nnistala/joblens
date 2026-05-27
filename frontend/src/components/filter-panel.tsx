"use client";

import { useState, useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "@/lib/utils";

const JOB_TYPES = [
  { value: "full_time", label: "Full Time" },
  { value: "part_time", label: "Part Time" },
  { value: "contract", label: "Contract" },
  { value: "internship", label: "Internship" },
];

const WORK_MODES = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "Onsite" },
];

export interface FilterValues {
  job_type: string[];
  work_mode: string[];
  experience_min: string;
  experience_max: string;
  salary_min: string;
  skills: string[];
}

interface FilterPanelProps {
  initialValues?: Partial<FilterValues>;
  onApply: (filters: FilterValues) => void;
  onClear: () => void;
  open?: boolean;
  onClose?: () => void;
}

const defaultFilters: FilterValues = {
  job_type: [],
  work_mode: [],
  experience_min: "",
  experience_max: "",
  salary_min: "",
  skills: [],
};

export default function FilterPanel({
  initialValues,
  onApply,
  onClear,
  open,
  onClose,
}: FilterPanelProps) {
  const [filters, setFilters] = useState<FilterValues>({
    ...defaultFilters,
    ...initialValues,
  });
  const [skillInput, setSkillInput] = useState("");

  useEffect(() => {
    setFilters({ ...defaultFilters, ...initialValues });
  }, [initialValues]);

  const toggleCheckbox = (
    key: "job_type" | "work_mode",
    value: string
  ) => {
    setFilters((prev) => {
      const arr = prev[key];
      return {
        ...prev,
        [key]: arr.includes(value)
          ? arr.filter((v) => v !== value)
          : [...arr, value],
      };
    });
  };

  const addSkill = () => {
    const skill = skillInput.trim();
    if (skill && !filters.skills.includes(skill)) {
      setFilters((prev) => ({ ...prev, skills: [...prev.skills, skill] }));
    }
    setSkillInput("");
  };

  const removeSkill = (skill: string) => {
    setFilters((prev) => ({
      ...prev,
      skills: prev.skills.filter((s) => s !== skill),
    }));
  };

  const handleClear = () => {
    setFilters(defaultFilters);
    setSkillInput("");
    onClear();
  };

  const content = (
    <div className="space-y-6">
      {/* Job Type */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-gray-900">Job Type</h3>
        <div className="space-y-2">
          {JOB_TYPES.map((type) => (
            <label
              key={type.value}
              className="flex cursor-pointer items-center gap-2"
            >
              <input
                type="checkbox"
                checked={filters.job_type.includes(type.value)}
                onChange={() => toggleCheckbox("job_type", type.value)}
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">{type.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Work Mode */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-gray-900">Work Mode</h3>
        <div className="space-y-2">
          {WORK_MODES.map((mode) => (
            <label
              key={mode.value}
              className="flex cursor-pointer items-center gap-2"
            >
              <input
                type="checkbox"
                checked={filters.work_mode.includes(mode.value)}
                onChange={() => toggleCheckbox("work_mode", mode.value)}
                className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">{mode.label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Range */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-gray-900">
          Experience (years)
        </h3>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min="0"
            placeholder="Min"
            value={filters.experience_min}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, experience_min: e.target.value }))
            }
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <span className="text-gray-400">-</span>
          <input
            type="number"
            min="0"
            placeholder="Max"
            value={filters.experience_max}
            onChange={(e) =>
              setFilters((prev) => ({ ...prev, experience_max: e.target.value }))
            }
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Salary Minimum */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-gray-900">
          Minimum Salary (LPA)
        </h3>
        <input
          type="number"
          min="0"
          placeholder="e.g. 500000"
          value={filters.salary_min}
          onChange={(e) =>
            setFilters((prev) => ({ ...prev, salary_min: e.target.value }))
          }
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>

      {/* Skills */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-gray-900">Skills</h3>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add a skill"
            value={skillInput}
            onChange={(e) => setSkillInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                addSkill();
              }
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
          />
          <button
            type="button"
            onClick={addSkill}
            className="shrink-0 rounded-lg bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Add
          </button>
        </div>
        {filters.skills.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            {filters.skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-0.5 text-xs font-medium text-primary-700"
              >
                {skill}
                <button
                  onClick={() => removeSkill(skill)}
                  className="hover:text-primary-900"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={() => onApply(filters)}
          className="flex-1 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          Apply Filters
        </button>
        <button
          type="button"
          onClick={handleClear}
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Clear
        </button>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden w-72 shrink-0 lg:block">
        <div className="sticky top-20 rounded-xl border border-gray-200 bg-white p-5">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Filters</h2>
          {content}
        </div>
      </aside>

      {/* Mobile drawer */}
      {open !== undefined && (
        <div
          className={cn(
            "fixed inset-0 z-50 lg:hidden",
            open ? "visible" : "invisible"
          )}
        >
          <div
            className={cn(
              "absolute inset-0 bg-black/40 transition-opacity",
              open ? "opacity-100" : "opacity-0"
            )}
            onClick={onClose}
          />
          <div
            className={cn(
              "absolute bottom-0 left-0 right-0 max-h-[80vh] overflow-y-auto rounded-t-2xl bg-white p-6 transition-transform",
              open ? "translate-y-0" : "translate-y-full"
            )}
          >
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-semibold text-gray-900">Filters</h2>
              <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            {content}
          </div>
        </div>
      )}
    </>
  );
}
