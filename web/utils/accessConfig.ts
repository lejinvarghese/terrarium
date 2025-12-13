/**
 * Access Code Configuration
 *
 * This file manages valid access codes for secure areas.
 * In production, consider moving these to environment variables
 * or a secure backend API endpoint.
 */

export interface AccessRoute {
  id: string;
  url: string;
  title: string;
  codes: string[];
}

// Default access codes - can be overridden via environment variables
const DEFAULT_CODES = [
  'UNDERGROWTH',
  'TERR4R1UM',
  'CYB3RN3T1C',
  'SW4RM',
  'ECLIPSE',
];

// Access-controlled routes configuration
export const ACCESS_ROUTES: AccessRoute[] = [
  {
    id: 'engine',
    url: '/engine',
    title: 'ENGINE ACCESS',
    codes: process.env.NEXT_PUBLIC_ENGINE_CODES?.split(',') || DEFAULT_CODES,
  },
  {
    id: 'library',
    url: '/library',
    title: 'LIBRARY ACCESS',
    codes: process.env.NEXT_PUBLIC_LIBRARY_CODES?.split(',') || DEFAULT_CODES,
  },
];

/**
 * Validates an access code against a list of valid codes
 */
export function validateAccessCode(code: string, validCodes: string[]): boolean {
  const normalizedCode = code.trim().toUpperCase();
  const normalizedValidCodes = validCodes.map(c => c.trim().toUpperCase());
  return normalizedValidCodes.includes(normalizedCode);
}

/**
 * Get access route configuration by ID
 */
export function getAccessRoute(routeId: string): AccessRoute | undefined {
  return ACCESS_ROUTES.find(route => route.id === routeId);
}

/**
 * Check if a code is valid for a specific route
 */
export function isValidForRoute(code: string, routeId: string): boolean {
  const route = getAccessRoute(routeId);
  if (!route) return false;
  return validateAccessCode(code, route.codes);
}

/**
 * Get all valid codes (useful for development/testing)
 * WARNING: Don't expose this in production!
 */
export function getAllCodes(): string[] {
  if (process.env.NODE_ENV === 'production') {
    console.warn('getAllCodes() should not be used in production');
    return [];
  }
  return DEFAULT_CODES;
}
