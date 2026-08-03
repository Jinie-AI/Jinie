"""Generates shared frontend utility files: validation, formatting, and API
helpers.
"""

from __future__ import annotations

from ..file_writer import FileWriter


class UtilitiesGenerator:
    """Generates the project's shared TypeScript utility files."""

    def __init__(self, writer: FileWriter) -> None:
        self._writer = writer

    # -- utilities ------------------------------------------------------
    def generate_utilities(self) -> None:
        self._writer.write(
            "src/utils/validation.ts",
            r"""export function isEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

export function isPhoneNumber(phone: string): boolean {
  const phoneRegex = /^[\d\s\-+()]{10,}$/;
  return phoneRegex.test(phone);
}

export function isEmpty(value: unknown): boolean {
  if (value === undefined || value === null || value === '') return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value as object).length === 0;
  return false;
}
""",
        )
        self._writer.write(
            "src/utils/format.ts",
            """export function formatDate(date: Date, _format: string = 'MM/DD/YYYY'): string {
  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  };
  return new Intl.DateTimeFormat('en-US', options).format(date);
}

export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}

export function truncateString(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.substring(0, Math.max(0, length - 3)) + '...';
}
""",
        )
        self._writer.write(
            "src/utils/api.ts",
            """import Constants from 'expo-constants';

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? (Constants.expoConfig?.extra?.apiUrl as string | undefined) ?? 'http://localhost:3000';

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export async function apiCall<T = unknown>(
  endpoint: string,
  method: string = 'GET',
  data?: unknown,
  headers?: Record<string, string>,
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  });

  if (!response.ok) {
    throw new ApiError(`HTTP ${response.status}: ${response.statusText}`, response.status);
  }

  return (await response.json()) as T;
}
""",
        )
